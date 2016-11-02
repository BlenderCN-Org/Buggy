#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## hit_parade.py

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


from collections import OrderedDict
from bge import logic as gl

'''This script run only once, text are set in prop of obj, and doesn't change'''

def main():
    scene = gl.getCurrentScene()
    objList = scene.objects
    pilotes = objList['pilotes']
    temps = objList['temps']

    if not gl.server:
        gl.loadGlobalDict()
        ##players = { "Aaa": [1, 1, 1, 1, 1, 0],
                    ##"Bbb": [2, 1, 1, 1, 2, 0]}
        players = gl.globalDict["players"]
    else:
        # le classement vient du server
        # gl.classement = ["toto", 10, "tutu", 19]
        players = {}
        try:
            # en mode server, le temps total est le temps du niveau seul
            # sa position dans la liste des temps n'a pas d'importance
            nb = int(len(gl.classement)/2) # nombre de joueurs classés
            # "t", 12, "g", 56
            for i in range(nb):
                players[gl.classement[2*i]] = [gl.classement[2*i+1], 0, 0, 0, 0, 0]
        except:
            players = {"Pb in server": [1, 1, 1, 1, 1, 0]}
        print(gl.classement)

    # Calcul du temps global somme des 5 premiers
    for k in players.keys():
        # Calcul du temps global somme des 5 premiers
        # Reset car bug
        players[k][5] = 0
        # Somme
        for i in range(5):
            players[k][5] += players[k][i]

    # tri par la valeur
    players_sorted = OrderedDict(sorted(players.items(), key=lambda item: item[1][5]))
    print(players_sorted)
    # Set prop Text in objects
    # J'en garde 4 à afficher
    n = 0
    pilotes['Text'] = ""
    temps['Text'] = ""

    for k, v in players_sorted.items():
        pilotes['Text'] = pilotes['Text'] + str(k) + "\n\n"
        temps['Text']   = temps['Text']   + str(players_sorted[k][5]) + "\n\n"
        n += 1
        if n == 4:
            break

main()
