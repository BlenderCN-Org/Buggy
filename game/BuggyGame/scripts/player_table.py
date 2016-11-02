#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## player_table.py

#############################################################################
# Copyright (C) Labomedia March 2011:2015
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franproplin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#############################################################################


from bge import logic as gl

"""Crée une table qui permet d'attribuer un mode de controle des buggys.
Wheel n'est possible qu'avec un serveur.
"""


def player_table_local(joy, nb):
    """pulse = 1
    Create a table with players number and joysticks number:
        Without joysticks, 2 players can play
        With 1 joysticks, 3 players can play
        With 2 joysticks, 4 players can play
        """

    if nb == 1:
        if joy > 0:
            gl.playerTable = ["J1", -1, -1, -1]
        else:
            gl.playerTable = ["A", -1, -1, -1]
    if nb == 2:
        if joy == 2:
            gl.playerTable = ["J1", "J2", -1, -1]
        elif joy == 1:
            gl.playerTable = ["J1", "A", -1, -1]
        elif joy == 0:
            gl.playerTable = ["A", "Z", -1, -1]
    if nb == 3:
        if joy == 2:
            gl.playerTable = ["J1", "J2", "A", -1]
        elif joy == 1:
            gl.playerTable = ["J1", "A", "Z", -1]
        else:
            print("Il faut au moins 1 manette pour jouer à 3")
            print("Le nombre de joueur passe à 2")
            gl.number_of_players = 2
            if joy == 2:
                gl.playerTable = ["J1", "J2", -1, -1]
            elif joy == 1:
                gl.playerTable = ["J1", "A",-1, -1]
            elif joy == 0:
                gl.playerTable = ["A", "Z", -1, -1]
    if nb == 4:
        if joy == 2:
            gl.playerTable = ["J1", "J2", "A", "Z"]
        else:
            print("Il faut au moins 2 manettes pour jouer à 4")
            if joy == 1:
                print("Le nombre de joueur passe à 3")
                gl.number_of_players = 3
                if joy == 1:
                    gl.playerTable = ["J1", "A", "Z", -1]
            else:
                print("Il faut au moins 1 manette pour jouer à 3")
                print("Le nombre de joueur passe à 2")
                gl.number_of_players = 2
                if joy == 2:
                    gl.playerTable = ["J1", "J2", -1, -1]
                elif joy == 1:
                    gl.playerTable = ["J1", "A", -1, -1]
                elif joy == 0:
                    gl.playerTable = ["A", "Z", -1, -1]

def player_table_server(joy):
    """
    pulse = 1
    Avec un serveur, seulement 1 seul joueur par PC:
        - Wheel est prioritaire sur les joysticks ou le clavier
    """

    # Save old table
    playerTable_old = gl.playerTable

    gl.playerTable = [-1,-1,-1,-1]
    # I read gl.cars to get cars position from server
    for k, v in gl.cars.items():
        # ex:
        # v["position"]=0 --> gl.playerTable[0] = 0
        # v["position"]=1 --> gl.playerTable[1] = 1
        # La table devient: [0, 1, -1, -1]
        gl.playerTable[v["position"]] = v["position"]

    # Ici je suis juste : gl.playerTable = [0, 1, -1, -1]
    # et je suis à gl.myPosition

    ### connected = liste des ip connectées
    ##connected = []
    ##if len(gl.cars) > 0:
        ##for k in gl.cars.keys():
            ##connected.append(k)
    ##if not gl.myIp in connected:
        ##gl.myPosition = len(gl.cars) + 1

    # Je défini la table
    if joy == 0:
        gl.playerTable[gl.myPosition] = "A"
    if joy >= 1:
        gl.playerTable[gl.myPosition] = "J1"
    if gl.wheel == 1:
        gl.playerTable[gl.myPosition] = "W"

    # Comparaison old and new pour réactiver des voitures si besoin
    # la réactivation ne concerne pas les copies de position du serveur
    for i in range(4):
        if playerTable_old[i] == -1:
            if gl.playerTable[i] in ["A", "Z", "J1", "J2", "W"]:
                gl.reactive[i] = 1
                print("Car ", i, "reactivated in player_table.py", "table old=",
                                playerTable_old, "table new=", gl.playerTable)
