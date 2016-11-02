#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## master_init.py

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

import sys
from bge import logic as gl

print("\n Buggy2.66 \n Copyright Labomedia \n\n")

''' Blender current directory = directory with *.blend
    Python  current directory = directory of the script
    Set this path is compulsory on debian not on ubuntu
'''

p = gl.expandPath("//")

path_list = [   "scripts",
                "cars/car00",
                "cars/car01",
                "cars/car02",
                "cars/car03"    ]

for i in path_list:
    sys.path.append(p + i)

print("Current directory =", p)
print("Python sys.path =", sys.path)

try:
    from scripts.tempo import Tempo
    from scripts.sound import EasyAudio
    from scripts.joystick import Joystick
    from sometools import get_my_ip
except:
    print("Check if scripts directory is in sys.path")

def main():
    gl.master_init = True # Used only in carApply.py
    init_variable()
    init_bgeconf()
    init_tempo()
    init_joystick()
    init_audio()
    music_loop()
    set_settings()

def init_tempo():
    # Création des objects
    gl.tempo_liste = [  ("print", 120),
                        ("always", -1),
                        ("race", -1),
                        ("end", 1000),
                        ("scene_change", -1)]

    gl.tempoDict = Tempo(gl.tempo_liste)
    gl.tempoDict["end"].lock()
    gl.tempoDict["race"].lock()
    gl.tempoDict["scene_change"].lock()

def init_variable():
    gl.my_name = "Mon nom provisoire"
    gl.state = 0 # Game State: Menus, Run, HitParade ...
    gl.carDict = {} # Dict des objets voiture
    gl.cars = {} # Dict
    gl.number_of_players = 0
    gl.level = 0
    gl.play = 0
    gl.time = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                [0, 0, 0, 0], [0, 0, 0, 0]]

    gl.playerTable = [0, 0, 0, 0]

    # Valeur par défaut pour le réseau
    gl.server = False  # True if server is running
    gl.network = False  # init in network.py
    gl.ipServer = "127.0.0.1"
    gl.myIp = get_my_ip()
    gl.portIn = 9999
    gl.portOut = 8888
    gl.multicastip = "224.0.0.11"
    gl.multicastport = 18888

    # mon nom est dans la liste data["phone"]: je joue avec un téléphone
    gl.wheel = 0
    gl.phone = [0, 0, 0] # acc, accel, brake

    gl.tuning = {   "adherence": 50,
                    "amortissement": 50,
                    "puissance": 50,
                    "raideur": 50,
                    "roulis": 50}

    gl.send_to_server = False
    gl.myPosition = 0  # on starting line 0 to 3
    gl.reactive = [0, 0, 0, 0]
    gl.reset = 0
    gl.start = 0
    gl.classement = []
    gl.rot_liss = [[], []]
    gl.rot = [-0.01, 0, 0]
    print("Init Variable in master_init")

def init_joystick():
    gl.joystickOPY = Joystick()
    joy = gl.joystickOPY.joy_number
    print(joy, gl.joysticks)

def init_audio():
    gl.music = EasyAudio(["BlueScorpion"], "//samples/")

def music_loop():
    gl.music["BlueScorpion"].repeat(0.5)

def set_settings():
    '''Dict to use joystick settings for all car
       Key example with car00: p = gl.settings[("car00", "Power")]
       TODO pourquoi ça ne vient pas des ini ?
    '''
    settings = {}

    for c in range(4):
        # Set Suspension Compression
        settings[(c, "SuspComp")] = 10.0
        # Set Suspension Damping
        settings[(c, "SuspDamp")] = 100.0
        # Set Suspension Stiffness
        settings[(c, "SuspStiff")] = 100.0
        # Set Roll Influence
        settings[(c, "Roll")] = 0.05
        # Set Tyre Friction
        settings[(c, "TyreFrict")] = 5.0
        # Set Power
        settings[(c, "Power")] = 500  # 500

    gl.settings = settings

def init_bgeconf():
    # If not bgeconf file, this create it
    try:
        gl.loadGlobalDict()
        # Don't delete the below line !
        print("This Print create bgeconf file, however no exception.",
                                                        gl.globalDict["Buggy"])
        #print(gl.globalDict["players"])
    except:
        players = {}
        ##players = { "Aaa": [99999, 99999, 99999, 99999, 99999, 99999],
                    ##"Bbb": [99998, 99998, 99998, 99998, 99998, 99998],
                    ##"Ccc": [99997, 99997, 99997, 99997, 99997, 99997],
                    ##"Ddd": [99996, 99996, 99996, 99996, 99996, 99996]}
        gl.globalDict["players"] = players
        gl.globalDict["Buggy"] = "Have Fun !"
        gl.saveGlobalDict()
