#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## buggygame.py

#############################################################################
# Copyright (C) Labomedia 2011:2015
#
#    This file is part of Buggy.
#
#    Buggy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Buggy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################


from collections import OrderedDict
from time import time, sleep
import json
import ast

from subprocess import Popen, PIPE


class Game:
    """Game Management:

    with all cars datas, all phones datas,
    head rotation, with GUI or not.

    """

    def __init__(self):
        # Ce qui est répondu par le serveur, type bytes, donc json encodé
        self.svr_resp = None
        # Le serveur répond (True) ou pas(False)
        self.resp = True
        # Dict des datas de chaque joueur dans blender
        self.players = OrderedDict()
        # les datas reçues de tous les téléphones
        self.phone = {}

        # Liste des connectés avec leur adresse ip
        self.connected_blender = []
        self.connected_phone = []

        # Gestion du jeu
        self.reset = 0
        self.start = 1
        self.level = 3

        # Liste des adresse ip dans l'ordre
        self.classement = []
        self.top = time()

        # Pour la définition de qui est dictateur
        self.dbv_exist = 0
        self.dbv_name = ""

        # Subprocess
        self.subpr = None
        self.blender_gui_start()

    def dbv_management(self):
        """Gestion du dictateur:
        - gestion du GUI local
        - Si list des téléphones connectés:
                - vide : local gui
                - sinon: le premier de la liste est dictateur
        """

        if len(self.connected_phone) > 0:
            self.dbv_exist = 1
            self.dbv_name = self.connected_phone[0]
        else:
            self.dbv_exist = 0
            self.dbv_name = ""

        ## GUI local
        # Pas de dictateur; local GUI
        if self.dbv_exist == 0:
            # Local GUI
            self.blender_gui_start()
        # Dictateur
        if self.dbv_exist == 1:
            # Pas de local GUI
            self.blender_gui_stop()

    def dbv_verif(self):
        # Vérification que le dictateur est dans les téléphones connectés
        if not self.dbv_name in self.connected_phone:
            print("Check if dictateur in phone dict")
            self.dbv_exist = 0
            self.dbv_name = ""
        print("Dictateur:{} Connected phone{}".format(self.dbv_name,
                                                    self.connected_phone))

    def sorting_messages(self, message, addr):
        """Récupéation des data dans le json reçu,
        répartition dans les dict, crétion de la réponse ou pas.
        """

        msg = ast.literal_eval(message.decode("utf-8"))

        if "From server GUI" in msg:
            # Gestion du jeu
            self.msg_server_gui(msg["From server GUI"])

        if "phone" in msg:
            # msg des téléphones
            self.msg_phone(msg["phone"])

        if "joueur" in msg:
            # msg des joueurs dans blender
            self.msg_joueur(msg["joueur"], addr)

        if "Give me players list and dictateur" in msg:
            # Retourne la liste de tous les joueurs connectés su le serveur
            self.resp_players_list_and_dictateur()

        if "Game" in msg:
            # Reception de Game venu d'un phone
            # msg["game"] = {"reset": 0, "start": 0, "level": 1}
            self.msg_game(msg["Game"])

        # Print pour debug
        self.print_some()

    def print_some(self):
        # Print pour le suivi
        if time() - self.top > 1:
            print("Nom des joueurs blender", self.connected_blender)
            print("Nom des téléphones connectés"  , self.connected_phone)
            if self.dbv_name == "":
                name = "Empty string"
            else:
                name = self.dbv_name
            print("Dictateur:", name)
            print("Rotation", "rien")
            self.top = time()

    def resp_players_list_and_dictateur(self):
        """Crée la réponse à la demande de la liste des joueurs
        par un téléphone.
        """
        self.resp = True
        players_list = []
        for key, val in self.players.items():
            if 'name' in val['car']:
                name = val['car']['name']
                players_list.append(name)

        msg = { "Liste des joueurs": players_list,
                "Dictateur": { "dbv_exist": self.dbv_exist,
                               "dbv_name": self.dbv_name}}

        # {"Liste des joueurs": ["serge"],
        #  "Dictateur": {"dbv_exist": 0, "dbv_name": ""}}
        self.svr_resp = json.dumps(msg).encode("utf-8")

    def msg_phone(self, data):
        """Mise à jour du dictionnaire des datas des téléphones,
        pas de réponse par le serveur. Gestion de DBV.
        """
        self.resp = False # pas de réponse par le serveur
        for name in data.keys():
            self.phone[name] = data[name]
            self.phone[name]['insert'] = int(time())
            if self.dbv_exist == 0:
                self.dbv_exist = 1
                self.dbv_name = name
        # DBV
        self.dbv_management()

    def msg_game(self, data):
        """Applique les valeurs de la gestion du jeu reçue d'un téléphone."""
        self.level = data["level"]
        self.start = data["start"]
        self.reset = data["reset"]

    def msg_server_gui(self, data):
        """Mise à jour des variables de l'état du jeu,
        pas de réponse par le serveur..
        """
        self.resp = False
        # {'reset': 0, 'start': 0, 'level': 1}
        self.level = data["level"]
        self.start = data["start"]
        self.reset = data["reset"]

    def msg_joueur(self, joueur, addr):
        """Appelé à la réception de data de blender,
        mise à jour des dict, puis réponse.
        """
        self.resp = True
        ip = addr[0]
        # Nouveau joueur
        if not ip in self.players:
            # Crée une clé dans le dict avec l'ip, la valeur est un dict
            self.players[ip] = {}
            # Crée un dict pour car
            self.players[ip]["car"] = {}
            # Je rempli
            self.set_player_data(joueur, ip)
            self.players[ip]["port"] = addr[1]
            self.set_position(ip)
        # Joueur existant
        else:
            self.set_player_data(joueur, ip)

        # Création de la réponse
        self.update_svr_resp()

    def set_position(self, ip):
        """Je reconstruit toutes les positions, ça perturbe le jeu,
        mais ce sera juste."""
        # popsition = position dans le dict
        p = 0
        for key, val in self.players.items():
            position = p
            val["position"] = position
            p += 1

    def set_player_data(self, joueur, ip):
        try:
            self.players[ip]["car"]["loc"] = joueur["loc"]
            self.players[ip]["car"]["rot"] = joueur["rot"]
            self.players[ip]["car"]["name"] = joueur["name"]
            self.players[ip]["car"]["time"] = joueur["time"]
            self.players[ip]["insert"] = int(time())  # on est pas à 1s près
        except:
            self.players[ip]["car"] = {}

    def blender_gui_start(self):
        if not self.subpr:
            self.subpr = Popen(['blenderplayer','server_GUI.blend'],
                                              stdout=PIPE)
            print("Server GUI start")
        pass

    def blender_gui_stop(self):
        if self.subpr:
            self.subpr.kill()
            self.subpr = None
            print("Server GUI stop")
        pass

    def update_connected_player(self):
        """Un joueur ou un téléphone qui n'envoie pas de data pendant 2 s
        est supprimé des dictionnaires.
        """

        # Reset puis je reconstruit les listes
        self.connected_blender = []
        self.connected_phone = []

        # Joueur blender
        # Je peux détruire pendant le parcours du dict: WARUM
        for ip in self.players.keys():
            try: # sinon erreur avec les datas incomplète au lancement du jeu
                # Récup du nom avec l'ip
                name = self.players[ip]["car"]["name"]
                if time() - self.players[ip]["insert"] > 2:
                    del self.players[ip]
                    print("I kill the player: ", ip)
                else:
                    self.connected_blender.append(name)
            except:
                pass

        # Phone
        # Je ne peux pas détruire pendant le parcours du dict
        name_to_delete = []
        for name in self.phone.keys():
            if time() - self.phone[name]["insert"] > 2:
                name_to_delete.append(name)
            else:
                self.connected_phone.append(name)
        # Je détruit les déconnectés
        for name in name_to_delete:
            del self.phone[name]
            print("I kill the phone: ", name)
            self.dbv_verif()
            self.dbv_management()

    def update_svr_resp(self):
        """Crée le message à envoyer à tous les joueurs dans Blender."""
        buggygame = {  "level": self.level,
                        "classement": self.classement,
                        "start": self.start,
                        "reset": self.reset }

        alldata = { "players": self.players,
                    "buggygame": buggygame,
                    "phone": self.phone}

        self.svr_resp = json.dumps(alldata).encode("utf-8")

    def reset_data(self):
        self.players = {}
        print("Reset des joueurs ...")


if __name__ == "__main__":
    # only to test this script
    # instance of class
    game = Game("/dev/ttyACM2", "LSM303")

    m1 = {"joueur": {"time": time(), "name": "brian", "loc": [0, 0, -5],
          "rot": [1, 0, 0, 0, 1, 0, 0, 0, 1]}}
    m1_json = json.dumps(m1).encode("utf-8")

    m2 = {"joueur": {"time": time(), "name": "john", "loc": [0, 0, -5],
          "rot": [1, 0, 0, 0, 1, 0, 0, 0, 1]}}
    m2_json = json.dumps(m2).encode("utf-8")

    game.sorting_messages(m1_json, ("192.168.1.89", 56123))
    game.sorting_messages(m2_json, ("192.168.1.11", 25600))

    game.update_svr_resp()

    sd = ast.literal_eval(game.svr_resp.decode("utf-8"))
    a = 0
    for k, v in sd.items():
        print("\n player" + str(a), k, v)
        a += 1
    print("\n\n")
    print("\n server data", game.svr_resp.decode("utf-8"))

    print("\n connected", game.connected_blender, game.connected_phone)

    print("\n players", game.players)

    game.update_svr_resp()
    print("\n players", game.players)

    players = { '192.168.1.5': { 'insert': 301,
                                'car': {'name': 'toto', 'time': 0, 'loc': [1.5, -2.4, 0.72],
                                        'rot': [[1.0, 0, 0], [0, 0.99, 0.02], [0, -0.02, 0.99]] },
                                'port': 56251,
                                'position': 0},
                '192.168.1.4': { 'insert': 301,
                                'car': {'name': 'titi', 'time': 0, 'loc': [1.5, -2.4, 0.72],
                                        'rot': [[1.0, 0, 0], [0, 0.99, 0.02], [0, -0.02, 0.99]] },
                                'port': 56221,
                                'position': 1}
                }

    ##r = []
    ##for key, val in players.items():
        ##n = val['car']['name']
        ##r.append(n)
    ##print(r)

    game.resp_players_list_and_dictateur()
