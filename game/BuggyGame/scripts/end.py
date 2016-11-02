#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## end.py

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
from bge import render
from scripts.sometools import scene_change

def control_and_end_during_race(objDict):
    # fin = 1111 at the beginning, +1 or +10 or +100 or +1000 near Empty_control
    # and idem at the finished line
    # +1 if car0, +10 if car1, +100 if car2, +1000 if car3
    for key in objDict.keys():
        if "Monolythe" in key:
            # fin is always >= 1111
            # because all cars must be near Monolythe befor starting
            fin = objDict[key]["fin"]
            l = list(str(fin))
            # The "car0i" has finished only if l[i] = 3
            # fin = 1111 --> cars on starting line
            if fin > 1111:
                for c in range(4):
                    if l[c] == "3":
                        # car ended this level but ordre est inversé
                        car_end(objDict, 3-c)
                # à partir de fin = 1112
                if not gl.server:
                    level_end(objDict, fin)
                else:
                    level_end_server(objDict, fin)

def car_end(objDict, c):
    # Save time, display this time, if the car c finished
    # gl.level - 1 because gl.level begin at 1 and mot 0, c = 0 to 3
    # Si je ne suis pas passé, le temps = 0
    # Le temps sera =! 0 une fois passé ici, donc je ne passe ici qu'une fois
    if gl.time[gl.level - 1][c] == 0:
        # Get time
        t = objDict["TimerSecond0" + str(c)]["Text"]
        # Display on hud
        objDict["Info0" + str(c)]["Text"] = "Time = " + str(t)
        objDict["Info0" + str(c)].resolution = 64
        # Save in gl
        gl.time[gl.level - 1][c] = t
        # Save in bgeconf lfile
        gl.globalDict["players"][gl.my_name][gl.level - 1] = t
        gl.saveGlobalDict()
        print("Car{0} finished Race{1} at {2}".format(c, gl.level, t))

def level_end(objDict, fin):
    # Level ended if fin = 3 for all running cars
    nb = gl.number_of_players
    # if 2 cars, end if fin = 1133 or 2233, 2 is impossible but in true life !
    l = list(str(fin))
    how_many_finished = 0
    for j in range(nb):
        if l[3-j] == "3":
            how_many_finished += 1

    if how_many_finished == nb:
        gl.level += 1
        # Fin des 5 niveaux
        if gl.level > 5:
            gl.level = 0
            del gl.carDict
            gl.carDict = {}
            stop_sound()
            print("Race5 finished. Return to HitParade")
            scene_change("Race5", "HitParade")
            gl.state = "HitParade"
            render.setBackgroundColor([0.0, 0.5, 1, 1])
            gl.tempoDict["race"].reset()
            gl.tempoDict["race"].lock()
        # Fin du niveau
        else:
            scene_change("Race" + str(gl.level - 1), "Race" + str(gl.level))
            print("Go to scene Race{0}".format(gl.level))
            gl.tempoDict["race"].reset()
            del gl.carDict
            gl.carDict = {}
            stop_sound()
            print("All car pyhton objets are deleted")

def level_end_server(objDict, fin):
    # Level ended if fin = 3 for my car
    l = list(str(fin))
    if l[gl.myPosition] == "3":
        if gl.classement != 0:
            gl.carDict = {}
            stop_sound()
            print("Level {} finished. Return to HitParade".format(gl.level))
            scene_change("Race" + str(gl.level), "HitParade")
            gl.state = "HitParade"
            render.setBackgroundColor([0.0, 0.5, 1, 1])
            gl.tempoDict["race"].reset()
            gl.tempoDict["race"].lock()

def stop_sound():
    try:
        gl.motorSound[0]["son_moteur"].stop()
        gl.motorSound[1]["son_moteur"].stop()
    except:
        pass

def end_scene(scenes, this_scene):
    '''Delete this_scene'''
    for scn in scenes:
        if scn.name == this_scene:
            scn.end()
            print("End of scene:", scn)
