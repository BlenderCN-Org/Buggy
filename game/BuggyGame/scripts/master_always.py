#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## master_always.py

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


"""
Lancé à chaque frame.
Fait tourner le jeu.

"""


import sys
from bge import logic as gl
from bge import render
from bge import events

# Bidouille pour définir les chemin
path = gl.expandPath("//BuggyGame")
sys.path.append("/scripts")

from scripts import network
from scripts.sound import EasyAudio
from scripts.viewport import enable_full_viewport, enable_half_viewport
from scripts.viewport import enable_stereo_viewport
from scripts.viewport import enable_quad_viewport, disable_viewport
from scripts.player_table import player_table_local, player_table_server
from scripts.joystickApply import joysticks_invert, joysticks_test_Menu, joysticks_Race
from scripts.end import control_and_end_during_race, car_end, level_end, end_scene
from scripts.extra import printSome, reset_hud, hud
from scripts.master_init import init_variable
from scripts.sometools import scene_change

def main():
    objDict = get_all_obj_in_dict()
    network.main()
    gl.joystickOPY.update()
    gl.tempoDict.update()
    printSome()
    player_table()

    # Once at the benning when Labomedia scene is finished
    if gl.tempoDict["always"].tempo == 180:
        gl.state = "InputName"

    if gl.state == "InputName":
        input_name(objDict)

    if gl.state == "Menu":
        menus(objDict)

    if gl.state == "Race":
        race(objDict)

    if gl.state == "HitParade":
        hit_parade(objDict)

    if gl.reset:
        reset(objDict)

def reset(objDict):
    try:
        print("Reset")
        # Reset de toutes les cam
        for i in ["00", "01", "02", "03"]:
            objDict["camCar" + i].useViewport = False
    except:
        print("Reset enable and cam disabled")

def hit_parade(objDict):
    try:
        if objDict["retourMenu"]["hit parade end"]:
            # Reset all variable
            init_variable()
            gl.state = "Menu"
            # Go to Menu
            scene_change("HitParade", "Menu")
    except:
        print("Problem in master_always line 70 because HitParade isn't loaded")

def input_name(objDict):
    ''' Labomedia scene is set with logic brick during 150,
    this is the first state = InputName. If cursor exist --> Scene = Name
    '''

    if "cursor" in objDict:
        # Entrée après saisie du nom
        if objDict["cursor"]["end"] == True:
            print("End in Name ok")
            scene_change("Name", "Menu")
            gl.state = "Menu"

def menus(objDict):
    ''' Set players number, manettes'''

    # Config joystick in Menus
    joysticks_invert(objDict)
    joysticks_test_Menu(objDict)

    if gl.tempoDict["race"].tempo == 0: # je ne passerai qu'une fois
        # End of Menu Scene
        if gl.play == 1 : # je viens de cliquer sur Jouer
            if not gl.server: # en local
                scene_change("Menu", "Race1")
                gl.tempoDict["race"].unlock()
            else:
                p = objDict["Patience"].worldPosition
                objDict["Patience"].worldPosition = [p[0], p[1], -0.8]
                if gl.level != 0:
                    scene_change("Menu", "Race" + str(gl.level))
                    gl.tempoDict["race"].unlock()

    # Set Race State
    if gl.tempoDict["race"].tempo == 60:
        gl.state = "Race"
        render.setBackgroundColor([0.0, 0.8, 1, 1])

def race(objDict):
    ''' Always in State Race. If RaceX loaded, cars run always'''

    # Only once at beginning

    # Display info 5 seconds
    if gl.tempoDict["race"].tempo == 120:
        hud(objDict)

    # Set race sound
    if gl.tempoDict["race"].tempo == 130:
        gl.music["BlueScorpion"].stop()
        # Lancement du ou des sons moteur. 1 son moteur par jeu.
        # Les sons ne sont pas lié à une voiture. L'appel de motor_sound()
        # dans car.py (qui retourne volume, pitch) lie à une voiture.

        gl.motorSound = EasyAudio(["son_moteur"], "//samples/")

        # Le moteur tourne toujours, même au clavier, au ralenti
        #if gl.joystickOPY.J1:
        gl.motorSound["son_moteur"].repeat()

    # Disable hud
    if gl.tempoDict["race"].tempo == 360:
        reset_hud(objDict)

    # Every 2 seconds
    if gl.tempoDict["race"].tempo % 120 == 0:
        set_viewport(objDict, gl.number_of_players)

    ## Always
    joysticks_Race(objDict)
    if gl.tempoDict["race"].tempo > 240:
        set_motor_sound(objDict)
    # Return on strating line if R
    R_status = gl.keyboard.events[events.RKEY]
    if R_status == gl.KX_INPUT_ACTIVE:
        cars_on_starting_line(objDict, gl.myPosition)

    # End
    control_and_end_during_race(objDict)

    # LAN Game
    if gl.server:
        gl.send_to_server = True
        # Block in strating line
        if gl.start == 0:
            for c in range(4):
                cars_on_starting_line(objDict, c)
        else:
            for i in range(4):
                objDict["car0" + str(i)].restoreDynamics()
        # Set good level with level send by server
        scenes = gl.getSceneList()
        for scn in scenes:
            if scn.name != "Master":
                if scn.name != "Race" + str(gl.level):
                    scene_change(scn.name, "Race" + str(gl.level))

def set_motor_sound(objDict):
    if not gl.server:
        if gl.joystickOPY.J1:
            apply_motor_sound(0, gl.joystickOPY.J1)

    if gl.server and gl.joystickOPY.J1 and gl.playerTable[0] == "J1":
        apply_motor_sound(gl.myPosition, gl.joystickOPY.J1)

    for i in range(4):
        # TODO: à vérifier, toujours en server, une seule voiture
        if gl.playerTable[i] == "W":
            accel = 0
            if gl.phone[0]:
                accel = gl.phone[1]/100
            else:
                accel = 0
            apply_motor_sound(gl.myPosition, accel)

def apply_motor_sound(car, J):
    ''' car = indice de la voiture qui retourne volume, pitch.'''
    upDown = 0

    if gl.playerTable[0] == "J1":
        upDown = J.joyOut[0]

    if gl.playerTable[gl.myPosition] == "W":
        upDown = J

    volume, pitch = gl.carDict[gl.myPosition].motor_sound(upDown)
    # pb si W:
    try:
        gl.motorSound["son_moteur"].set_volume(volume)
        gl.motorSound["son_moteur"].set_pitch(pitch)
    except:
        pass

def cars_on_starting_line(objDict, c):
    '''Cars are blocked on strating line'''
    # Time Reset for every cars
    objDict["TimerSecond0" + str(c)]["Text"] = 0

    if gl.server:
        for i in range(4):
            objDict["car0" + str(i)].suspendDynamics()

    # Set Loc Rot for every cars
    rot = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if c == 0:
        loc = [1.5, -3, 1.5]
        gl.carDict[0].set_Loc_Rot(loc, rot)
    if c == 1:
        loc = [-1.5, -9, 1.5]
        gl.carDict[1].set_Loc_Rot(loc, rot)
    if c == 2:
        loc = [1.5, -15, 1.5]
        gl.carDict[2].set_Loc_Rot(loc, rot)
    if c == 3:
        loc = [1.5, -21, 1.5]
        gl.carDict[3].set_Loc_Rot(loc, rot)

def set_viewport(objDict, nb):
    '''Set view with players number'''
    # 1 player  > full view
    if nb == 1:
        cam1 = objDict["camCar00"]

        if gl.server:
            objDict["camCar00"].useViewport = False
            cam1 = objDict["camCar0" + str(gl.myPosition)]
        enable_full_viewport(cam1)

    # 2 players > vertical split
    if nb == 2:
        cam1 = objDict["camCar00"]
        cam2 = objDict["camCar01"]
        enable_half_viewport(cam1, cam2)

    # 3 or 4 players > quad split
    if nb > 2:
        cam1 = objDict["camCar00"]
        cam2 = objDict["camCar01"]
        cam3 = objDict["camCar02"]
        if nb == 3:
            cam4 = objDict["camEnd"]
        else:
            cam4 = objDict["camCar03"]
        enable_quad_viewport(cam1, cam2, cam3, cam4)

def player_table():
    """pulse = 1 """
    joy = gl.joystickOPY.joy_number
    nb = gl.number_of_players
    if gl.server:
        gl.number_of_players = 1
        player_table_server(joy)
    else:
        player_table_local(joy, nb)

def get_all_obj_in_dict():
    ''' Get all blender objects from all scenes in a dict {object.name: object}.
        Very usefull but objDict is argument in all functions'''
    scenes = gl.getSceneList()
    objDict = {}
    for scn in scenes:
        for obj in scn.objects:
            objDict[obj.name] = obj

    return objDict
