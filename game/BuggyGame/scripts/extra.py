#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## extra.py

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
from scripts.sometools import print_str_args

"""
Fonctions appelées par les autres scripts:
    - hud pour affichage d'info tête haute
    - printSome pour déboggage
"""

def hud(objDict):
    for c in range(4):
        mode = gl.playerTable[c]
        obj = objDict["Info0" + str(c)]
        if not isinstance(mode, int):
            if mode == "A":
                obj["Text"] = "Vous jouez au clavier \n avec \n le pavé directionnel"
                obj.resolution = 64
            if mode[:1] == "J":
                obj["Text"] = "Vous jouez \n avec une manette"
                obj.resolution = 64
            if mode == "Z":
                obj["Text"] = "Vous jouez au clavier \ n avec \n les touches ZQSD"
                obj.resolution = 64
            if mode == "W":
                obj["Text"] = "Vous jouez avec \n Wheel"
                obj.resolution = 64

def reset_hud(objDict):
    for c in range(4):
        objDict["Info0" + str(c)]["Text"] = ""

def printSome():
    if gl.tempoDict["print"].tempo == 0:
        since = int(gl.tempoDict["always"].tempo / 60)
        print("\nBuggy Game is running since {0} seconds\n".format(since))
        print("Some variable to debug")
        print_str_args( "gl.carDict",
                        "gl.cars",
                        "gl.phone",
                        "gl.wheel",
                        "gl.my_name",
                        "gl.state",
                        "gl.playerTable",
                        "gl.myPosition",
                        "gl.ipServer",
                        "gl.server",
                        "gl.classement",
                        "gl.number_of_players",
                        "gl.reset",
                        "gl.start",
                        "gl.tuning",
                        "gl.rot")
