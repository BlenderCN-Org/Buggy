#! /usr/bin/env python3
# -*- coding: utf-8 -*-

## main.py

#############################################################################
# Copyright (C) Labomedia 2015
#
#    This file is part of Wheel.
#
#    Wheel is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Wheel is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################


__version__ = '11.00'

"""
11.00 aide complétée
10.03 suite test
10.02 ok mais latence ?
10.01 pas d'envoi
10.00 bug au lancement
"""


import os, sys
import socket
import fcntl
import struct
import json
import ast
from jnius import autoclass
from time import sleep, time
import threading

import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, NumericProperty


MCAST_ADDR = "224.0.0.11"
MCAST_PORT = 18888

def json_convert(data):
    """json de data, ok avec data de type int et str."""

    if isinstance(data, int):
        json_convert = json.dumps(str(data))
    if isinstance(data, float):
        json_convert = json.dumps(str(data))
    elif isinstance(data, dict):
        json_convert = json.dumps(data)
    elif isinstance(data, str) :
        json_convert = json.dumps(data).encode("utf-8")
    else:
        json_convert = json.dumps("Json error")
    return json_convert

def freq_to_periode(freq):
    """Retourne la période de la fréquence pour le sleep()."""
    # Maxi = 60 Hz
    if freq != 0:
        periode = 1.0 / float(freq)
        # Maxi 60 Hz
        if periode < 0.015:
            periode = 0.015
    # Mini = 1 Hz
    else:
        periode = 1.0
    return periode

def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                            ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = ["eth0", "eth1", "eth2", "wlan0", "wlan1", "wifi0",
                      "ath0", "ath1", "ppp0"]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

def get_server_msg():
    """Réception des messages du serveur en multicast."""

    # Multicast
    multi = MulticastReceiver(MCAST_ADDR, MCAST_PORT)
    multi.connexion()

    ip = ""
    ip_server_ok = False
    # Evite une boucle infinie si le serveur ne tourne pas
    loop = 0
    while not ip_server_ok:
        loop += 1
        sleep(0.20)
        mcast_msg = multi.receive()
        if mcast_msg:
            mcast_dec = ast.literal_eval(mcast_msg.decode("utf-8"))
            if 'Ip Adress' in mcast_dec:
                # IP
                ip = mcast_dec['Ip Adress']
        if ip != "":
            print("IP serveur = {}".format(ip))
            ip_server_ok = True
        if loop > 10:
            break
    return ip


class AndroidOnly(object):
    """Cette classe retourne l'accélération en y à la demande."""

    def __init__(self):
        self.hardware = None
        print("Platform = {}".format(sys.platform))

        # Il faut vérifier sur plusieurs téléphones: linux3
        if 'linux3' in sys.platform:
            try:
                self.hardware = autoclass('org.renpy.android.Hardware')
                self.hardware.accelerometerEnable(True)
            except:
                print("Pb with Android Hardware")

    def get_accy(self):
        """Retourne accélération sur y si existe."""
        try:
            # accy entier de - 700 à 700 en gros = volant formule 1
            accy = int(100 * self.hardware.accelerometerReading()[1])
        except:
            accy = 10
        return accy


class LED(Button):
    '''Custom button class for having his index and custom graphics defined in
    the .kv + highligh state that draw an hover when activated.
    '''
    index = NumericProperty(0)


class WheelScreen(Screen, FloatLayout):
    """Ecran pour conduire la voiture,
    avec accélérateur, changement de vitesse, préréglages.
    Le client UDP est dans cette classe, il est utilisé par tous les écrans.
    Envoi en continu à fréquence définie dans les options, de toutes les datas.
    """

    grid = ObjectProperty(None)
    gestion = StringProperty(None)
    debug_text = StringProperty(None)

    def __init__(self, **kwargs):
        super(WheelScreen, self).__init__(**kwargs)

        self.name_list = ["toto", "", "", ""]
        self.my_name = ""

        # Pression
        self.pression = 0
        self.accelerator = 0
        self.brake = 0
        # Stokage de 105 valeurs de pression
        self.stock = []
        # coeff pour p max = 100
        self.coeff = 25
        self.etal_in_progress = False

        # Réglages voitures
        self.tuning = { 0: {"adherence": 50,
                            "amortissement": 50,
                            "puissance": 50,
                            "raideur": 50,
                            "roulis": 50},
                        1: {"adherence": 50,
                            "amortissement": 50,
                            "puissance": 50,
                            "raideur": 50,
                            "roulis": 50}}
        self.preset = 0

        # Android pour les accélérations
        self.android = AndroidOnly()

        # IP serveur: adresse provisoire pour que ce __init__ se termine
        # et affiche un écran
        # La connexion se fera en cliquant sur who are you
        self.ip_server = ""

        # création du client
        self.clt = MyUdpClient()
        self.freq = self.get_freq()
        self.periode = freq_to_periode(self.freq)
        self.sd_loop = 1
        self.rcv_loop = 1
        self.receive_start = 0

        # Grille des LEDs
        self.btn = []  # Liste de 12
        for x in xrange(12):
            btn = LED(index=x, background_color=(0,1,0,1))
            self.btn.append(btn)
            self.grid.add_widget(btn)

        # Dictateur bienveillant à vie qui gère le jeu
        self.dbv_exist = 0
        self.dbv_name = "bidon"

        # Debug mode on android
        self.debug = 0
        if self.debug:
            self.debug_text = str(self.name_list[0])
        else:
            self.debug_text = "Buggy Wheel"

    def dictateur_apply(self):
        # Je désactive le bouton si je ne suis pas dictateur
        if self.dbv_exist == 1 and  self.dbv_name == self.my_name:
            self.btn_gestion_enable()
        else:
            self.btn_gestion_disable()

    def btn_gestion_enable(self):
        self.ids['gestion'].disabled = False

    def btn_gestion_disable(self):
        self.ids['gestion'].disabled = True

    def on_touch_move(self, touch):
        """Définit la pression, puis demande affichage LEDs."""
        # Pb avec if touch.pressure existe !!
        press = 0
        try:
            # Get pression
            press = touch.pressure
        except:
            pass
        self.pression = self.get_pressure(press)
        self.set_LED()

    def set_LED(self):
        """12 leds pour maxi = 100
            100/12 = 8.33
            100 --> 12
              0 --> 0
        """

        # Reset
        for i in range(12):
            self.btn[i].state = "normal"
        # 100/8.33 = 12.005
        if self.accelerator or self.brake:
            n_LED = int((self.pression + 3)/8.33)  # à 3% près
            for j in range(n_LED):
                self.btn[j].state = "down"

    def on_touch_up(self, touch):
        """Si le doigt est relevé, la pression retomde à 0."""
        self.pression = 0

    def get_pressure(self, pressure):
        """Calcul des coefficients pour avoir une pression entre 0 et 100,
        quelque soit le téléphone.
        """

        # pression de 0 à 100
        good_p = int(self.coeff * ((pressure * 100000) - 1))
        # Toujours entre 0 et 100
        if good_p > 100:
            good_p = 100
        if good_p < 0:
            good_p = 0
        return good_p

    def do_acc_release(self):
        self.disable_accelerator()
        self.pression = 0
        self.set_LED()

    def do_brake_release(self):
        self.disable_brake()
        self.pression = 0
        self.set_LED()

    def enable_accelerator(self):
        """Capture de pression sur l'accélérateur."""
        self.accelerator = 1

    def disable_accelerator(self):
        """Plus de capture de pression sur l'accélérateur."""
        self.accelerator = 0

    def enable_brake(self):
        """Capture de pression sur le frein."""
        self.brake = 1

    def disable_brake(self):
        """Plus de capture de pression sur le frein."""
        self.brake = 0

    def go_to_who(self):
        """"Appelé par on_press sur Who Are You."""

        manager = WheelApp.get_running_app().manager

        # Adresse ip qui vient du serveur en multicast
        # pour recevoir il faut envoyer une requête, donc il faut l'adresse
        self.ip_server = get_server_msg()

        if self.ip_server == "":
            info = "Le serveur ne tourne pas: \n\nLancez un jeu sur un PC\
            \n\nqui doit être sur le même routeur\
            \n\nque le téléphone ou tablette."
            manager.get_screen("Info").info = info
            # Je bascule sur Info, ça quitte cette fonction
            manager.current = ("Info")
        else:
            # J'ai une adresse serveur valide
            # Receive loop met à jour la liste du serveur en permanence
            # Application des noms reçus
            manager.get_screen("WhoAreYou").apply_server_name(self.name_list)
            manager.current = ("WhoAreYou")

    def send_with_name():
        """Thread d'envoi lancé par on_press sur valider dans who."""
        self.send_thread()

    def receive_loop(self):
        """Reçoit les réponses du serveur:
        - liste des noms des joueurs
        - message dictateur.
        """

        while self.rcv_loop:
            # Je reçois si j'envoie un ordre
            ordre = json_convert("Give me players list and dictateur")
            try:
                if self.ip_server != "":
                    if self.debug:
                        self.debug_text = self.ip_server
                    self.clt.client_send(ordre, self.ip_server, 8888)
                    print("envoi")
                else:
                    # je redemande d'adresse du serveur
                    self.ip_server = get_server_msg()
            except:
                pass

            sleep(0.50)  # j'attends un peu

            msgd = None
            try:
                msg = self.clt.client_received()
                if self.debug:
                    self.debug_text = str("reception ok")
                msgd = ast.literal_eval(msg.decode("utf-8"))
                print("reception")
            except:
                if self.debug:
                    self.debug_text = str("pas de reception")
                #print("Ressouce indisponible à la réception")
                pass

            if msgd:
                if "Liste des joueurs" in msgd:
                    self.name_list_apply(msgd["Liste des joueurs"])
                if "Dictateur" in msgd:
                    self.dictateur_msg_apply(msgd["Dictateur"])

    def receive_thread_start(self):
        """Lancement du thread de réception si on_press sur menu dans info
        mais une seule fois"""
        if not self.receive_start:
            print("Receive thread run")
            self.receive_start = 1
            self.receive_thread()

    def receive_thread(self):
        """Thread pour envoyer."""
        rcv_thread = threading.Thread(target=self.receive_loop)
        rcv_thread.start()

    def name_list_apply(self, msg):
        """Application du message reçu dans la liste des joueurs.
        Je complète a liste du serveur à len=4."""
        #self.debug_text = str(msg[0])
        # len(self.name_list) toujours 4 pour affichage
        for i in range(4 - len(msg)):
            msg.append("")
        self.name_list = list(msg)

    def dictateur_msg_apply(self, msgd):
        self.dbv_exist = msgd["dbv_exist"]
        self.dbv_name = msgd["dbv_name"]
        self.dictateur_apply()

    def get_freq(self):
        """Retourne la fréquence du fichier wheel.ini."""
        config = WheelApp.get_running_app().config
        freq = int(config.get('network', 'freq'))
        return freq

    def send_loop(self):
        '''Boucle infinie pour envoyer les datas à freq, freq defini dans les
        options. Envoi: accy, accelerator, brake.
        '''

        while self.sd_loop:
            msg = self.create_msg()

            try:
                self.clt.client_send(msg, self.ip_server, 8888)
            except:
                # Socket operations will raise a timeout exception
                # if the timeout period value has elapsed before
                # the operation has completed.
                pass

            # Tempo de la boucle
            sleep(self.periode)

    def send_thread(self):
        """Thread pour envoyer."""
        print("Send thread run")
        sd_thread = threading.Thread(target=self.send_loop)
        sd_thread.start()

    def create_msg(self):
        """Message envoyé par les téléphones."""
        accy = self.android.get_accy()  # entier, 10 si pas android
        name = self.my_name
        tune = self.tuning[self.preset]

        accel = 0
        frein = 0
        if self.accelerator:
            # self.pression de 0 à 100 dans blender
            accel = self.pression
        if self.brake:
            frein = self.pression

        gm =  WheelApp.get_running_app().manager.get_screen("Game")
        jeu = { "reset": gm.reset,
                "start": gm.start,
                "level": gm.level}

        msg = json_convert({ "phone": {name: { "accy":  accy,
                                            "accel": accel,
                                            "brake": frein,
                                            "tuning": tune}},
                          "Game": jeu})
        return msg

    def reset_freq(self, freq):
        self.freq = int(freq)
        self.periode = freq_to_periode(self.freq)

    def set_preset(self, i):
        """Numéro du preset."""
        self.preset = int(i)

    def do_aide(self):
        """"Appelé par on_press sur Aide."""

        manager = WheelApp.get_running_app().manager

        info = """
        Les PC doivent être sur le même routeur,
        les téléphones ou tablettes
        doivent être connectés en wifi sur ce même routeur.

        Vous pouvez régler la fréquence d'envoi dans les Options.

        Il faut bouger un peu le pouce pendant l'étalonnage,
        avec le pouce bien à plat.

        Si le texte du bouton Gestion du jeu est vert,
        vous gérer le jeu.
        Départ doit être actif pour que les voitures roulent.
        """

        manager.get_screen("Info").info = info
        # Je bascule sur Info, ça quitte cette class
        manager.current = ("Info")

    def do_quit(self):
        self.sd_loop = 0
        self.rcv_loop = 0
        sys.exit()


class WhoAreYouScreen(Screen):
    """Ecran qui permet de relier un téléphone à un PC particulier,
    en sélectionnant son nom dans la liste envoyé par le serveur.
    """

    # Voir http://kivy.org/docs/api-kivy.properties.html
    # Permet d'actualiser l'affichage si la valeur change
    # Nécessaire pour être appelée dans le kv
    # Les listes modifiées sont des copies, d'où risque d'affichage faux
    # d'où 4 variables pour éviter les erreurs et du temps perdu
    name0 = StringProperty()
    name1 = StringProperty()
    name2 = StringProperty()
    name3 = StringProperty()

    def __init__(self, **kwargs):
        super(WhoAreYouScreen, self).__init__(**kwargs)
        self.name0 = ""
        self.name1 = ""
        self.name2 = ""
        self.name3 = ""
        self.who = 0
        self.wheel = WheelApp.get_running_app().manager.get_screen("Wheel")

    def apply_server_name(self, name_list):
        """Appelé par on_press sur whoareyou dans Wheel pour afficher les noms
        qui viennent du seveur en continu dans le thread receive."""

        self.name0 = name_list[0]
        self.name1 = name_list[1]
        self.name2 = name_list[2]
        self.name3 = name_list[3]

    def players_list_to_name_list(self):
        """Appelé par on_press sur Valider dans WhoAreYou.
        Applique le nom sélectionné
        """
        my_name = self.wheel.name_list[self.who]
        print("Mon nom est {}".format(my_name))

        # Mise à jour dans wheel
        self.wheel.my_name = my_name

        # envoi dans wheel
        self.apply_send_with_name()

    def apply_send_with_name(self):
        """Avec le nom défini, envoi au serveur dans wheel."""
        wheel = WheelApp.get_running_app().manager.get_screen("Wheel")
        wheel.send_thread()

    def set_active(self, i, *args):
        self.who = i


class GameScreen(Screen):
    """Gestion du jeu, un seul téléphone a accès à cet écran."""

    # Ne pas oublier ça pour utilisation dans *.kv
    level = NumericProperty()

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.level = 1
        self.reset = 0
        self.start = 0

    def do_reset(self, state):
        """Mise à jour des variables."""
        if state == "down":
            self.reset = 1
        if state == "normal":
            self.reset = 0

    def do_start(self, state):
        """Mise à jour des variables."""
        if state == "down":
            self.start = 1
        if state == "normal":
            self.start = 0

    def do_level_moins(self):
        self.level -= 1
        if self.level == 0:
            self.level = 1
        if self.level == 6:
            self.level = 5

    def do_level_plus(self):
        self.level += 1
        if self.level == 0:
            self.level = 1
        if self.level == 6:
            self.level = 5


class PresetScreen(Screen):
    """Ecran qui permet de modifier les préréglages."""

    def __init__(self, **kwargs):
        super(PresetScreen, self).__init__(**kwargs)

    def on_slider(self, preset_indice, preset_name, instance, value):
        """Si un slider de réglage change, i est identifié par son iD,
        la valeur est appliquée dans tuning.
        """
        wheel = WheelApp.get_running_app().manager.get_screen("Wheel")
        # je récupère le dict de wheel, et je modifie
        tune = wheel.tuning

        # Je n'arrive pas à récupérer l'id du slider avec instance,
        # donc bidouille
        # entier de 0 à 100 pour limiter les longueurs des "print" !
        tune[preset_indice][preset_name] = int(value)

        # puis je retourne
        wheel.tuning = tune


class InfoScreen(Screen):
    """Retour d'info, aide, alerte."""

    # Ne pas oublier ça pour utilisation dans *.kv
    info = StringProperty()

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)

        self.info = "Sélectionner votre nom dans\n\n Who Are You ?\n\n\n\nPuis étalonner la pression de votre doigt dans\n\nEtalonnage."

    def on_press(self):
        # Lancement du thread de reception: liste des joueurs et dictateur
        manager = WheelApp.get_running_app().manager
        manager.get_screen("Wheel").receive_thread_start()

        sleep(1)

        # Go to Wheel
        manager.current = ("Wheel")


class EtalonnageScreen(Screen, FloatLayout):
    """Ecran d"étalonnage de la pression qui dépend
    de chaque téléphone ou tablette.
    """

    # Permet d'appeler grid_etal dans le kv
    grid_etal = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(EtalonnageScreen, self).__init__(**kwargs)

        # Grille des LEDs
        self.btn = []  # Liste de 12
        for x in xrange(12):
            btn = LED(index=x, background_color=(0,1,0,1))
            self.btn.append(btn)
            self.grid.add_widget(btn)

        self.pression = 0
        # True si bouton acc = on
        self.accel = False
        # Stokage de 105 valeurs de pression
        self.stock = []
        # coeff pour p max = 100
        self.coeff = 25

    def on_touch_move(self, touch):
        """Stocke 100 valeurs, calcul coeff."""
        press = 0
        try:
            if self.accel:
                # Pb avec if touch.pressure: !!
                press = touch.pressure
        except:
            pass
        # ajout jusqu'à avoir une liste de 100, à 100 le coeff est calculé
        if len(self.stock) < 101:
            self.stock.append(press)
        # Get pression
        self.pression = self.pression_et_coeff(press)
        self.set_LED()

    def pression_et_coeff(self, pressure):
        """Calcul d'un coefficient pour avoir une pression entre 0 et 100,
        quelque soit le téléphone.
        """

        # calcul coeff à 100 valeurs pour avoit pression = entier de 0 à 100
        if len(self.stock) == 100:
            self.stock.sort()
            # Je garde le plus grand
            p_max = self.coeff * ((self.stock[99] * 100000) - 1)
            # Correction du coeff
            self.coeff = int(100 * self.coeff / p_max)
        # pression de 0 à 100
        good_p = int(self.coeff * ((pressure * 100000) - 1))
        # Toujours entre 0 et 100
        if good_p > 100:
            good_p = 100
        if good_p < 0:
            good_p = 0

        return good_p

    def do_press(self):
        self.accel = True

    def do_etal_release(self):
        self.accel = False
        self.coeff_to_wheel()
        self.pression = 0
        self.stock = []
        self.set_LED()

    def coeff_to_wheel(self):
        """Applique le coeff dans wheel."""
        manager = WheelApp.get_running_app().manager
        manager.get_screen("Wheel").coeff = self.coeff

    def set_LED(self):
        """12 leds pour maxi = 100
            100/12 = 8.33
            100 --> 12
              0 --> 0
        """
        # Reset
        for i in range(12):
            self.btn[i].state = "normal"
        # Enable:
        n_LED = int((self.pression + 3)/8.33)  # à 3% près
        for j in range(n_LED):
            self.btn[j].state = "down"


# Liste des écrans, cette variable appelle les classes ci-dessus
# et doit être placée après ces classes
SCREENS = { 0: (InfoScreen,       "Info"),
            1: (WheelScreen,      "Wheel"),
            2: (WhoAreYouScreen,  "WhoAreYou"),
            3: (GameScreen,       "Game"),
            4: (PresetScreen,     "Preset"),
            5: (EtalonnageScreen, "Etalonnage")}


class MyUdpClient(object):
    """Simple UDP client from python socket documentation."""
    def __init__(self):
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Taille du buffer
        buffer_size = 1024
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        # if flag is 0, the socket is set to non-blocking
        #  In non-blocking mode, if a recv() call doesn’t find any data,
        # or if a send() call can’t immediately dispose of the data,
        # a error exception is raised; in blocking mode,
        # the calls block until they can proceed.
        #self.sock.setblocking(0)

        # Set a timeout on blocking socket operations.
        # If a float is given, subsequent socket operations will raise a
        # timeout exception if the timeout period value has elapsed before
        #the operation has completed.
        self.sock.settimeout(0.005)

    def client_send(self, data, host, port):
        """As you can see, there is no connect() call; UDP has no connections.
        Instead, data is directly sent to the recipient via sendto().
        data type is only str, json = str.
        """

        self.sock.sendto(data, (host, port))

    def client_received(self):
        received = self.sock.recv(1024)
        return received


class MulticastReceiver():
    """Récupère les datas reçues en Multicast."""
    def __init__(self, ip, port, buffer_size=1024, bavard=False):
        self.ANY = "0.0.0.0"
        self.MCAST_ADDR = ip
        self.MCAST_PORT = port
        self.sock = None
        self.buffer_size = buffer_size
        self.bavard = bavard

    def connexion(self):
        '''Création d'un socket multicast self.sock.'''
        # Création d'un socket
        try:
            #create a UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                        socket.IPPROTO_UDP)
            #allow multiple sockets to use the same PORT number
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            #Bind to the port that we know will receive multicast data
            self.sock.bind((self.ANY, self.MCAST_PORT))
            #tell the kernel that we are a multicast socket
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                                    255)
            #Tell the kernel that we want to add ourselves to a multicast group
            #The address for the multicast group is the third param
            status = self.sock.setsockopt(socket.IPPROTO_IP,
                                            socket.IP_ADD_MEMBERSHIP,
                                            socket.inet_aton(self.MCAST_ADDR)\
                                            + socket.inet_aton(self.ANY))
            self.sock.setblocking(0)
            # Limite la taille du buffer UDP pour éviter la latence,
            # le buffer est vidé à chaque lecture
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                    self.buffer_size)
            if self.bavard:
                print("Server receive on:")
                print("IP = {} : Port = {} with Buffer = {}\n".format(\
                        self.MCAST_ADDR, self.MCAST_PORT, self.buffer_size))
        except:
            print("No connection on IP={} Port={}".format(self.MCAST_ADDR,
                                                            self.MCAST_PORT))

    def receive(self):
        '''Return raw data received on multicast.'''
        raw_data = None
        try:
            raw_data = self.sock.recv(self.buffer_size)
            if self.bavard:
                print("Multicast data received = {0}".format(raw_data))
        except socket.error:
            if self.bavard:
                print("Nothing received in MulticastReceiver")
        return raw_data


class WheelApp(App):
    """Excécuté par __main__,
    app est le parent de cette classe dans kv.
    """

    def build(self):
        """Exécuté en premier après run()."""

        # Création des écrans
        self.manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
        return self.manager

    def build_config(self, config):
        '''Si le fichier *.ini n'existe pas,
        il est créé avec ces valeurs par défaut.
        Si il manque seulement des lignes, il ne fait rien !
        '''
        config.setdefaults('network',
                            {'freq': '30',})
        config.setdefaults('kivy',
                            {'log_level': 'debug',
                              'log_name': 'wheel_%y-%m-%d_%_.txt',
                              'log_dir': '/kivy',
                              'log_enable': '1'})
        config.setdefaults('postproc',
                            {'double_tap_time': '250',
                              'double_tap_distance': '20'})

    def build_settings(self, settings):
        """Construit l'interface de l'écran Options pour Wheel,
        les options Kivy sont par défaut,
        appelé par app.open_settings() dans .kv
        """

        data = '''[{"type": "title", "title": "Configuration du réseau"},
                   {"type": "numeric",
                    "title": "Fréquence d'envoi",
                    "desc": "Fréquence entre 1 et 60 Hz",
                    "section": "network", "key": "freq"}]'''

        # self.config est le config de build_config
        settings.add_json_panel('Wheel', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        '''Si modification des options, fonction appelée automatiquement.'''

        wheel = self.manager.get_screen("Wheel")

        if config is self.config:
            token = (section, key)
            # Si fréquence change
            if token == ('network', 'freq'):
                # Restart android with new frequency
                wheel.reset_freq(int(value))

    def go_mainscreen(self):
        '''Retour au menu principal depuis les autres écrans.'''
        self.manager.current = ("Wheel")

    def go_info(self):
        '''Retour au menu principal depuis les autres écrans.'''
        self.manager.current = ("Info")


if __name__ == '__main__':
    WheelApp().run()
