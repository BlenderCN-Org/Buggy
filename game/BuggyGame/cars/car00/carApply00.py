#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## carApply.py

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

from configparser import ConfigParser
import json
import mathutils

from bge import logic as gl
from car import Car
from joystick import Joystick
from sometools import droiteAffine

"""
Mandatory Name in blender:
    Example : car = 0 to 3
        In car00 directory
            - blend :       car00.blend
            - object car:   car00
            - Scene:        Car00
            - Tires:        tire0_00, tire1_00, tire2_00, tire3_00
            - Textures directory with all textures
            - car00.ini with car configuration
            - car.py

gl.cars =
{"192.168.1.4": {"insert": 1436799591,
                "position": 0,
                "car": {"loc": [150, -300, 142],
                        "time": 0,
                        "rot": [[100, 0, 0],
                                [0, 100, 0],
                                [0, 0, 100]],
                "name": "pc4"},
                "port": 39602},
"192.168.1.8": {"insert": 1436799591,
                "position": 1,
                "car": {"loc": [-149, -963, 397],
                        "time": 0,
                        "rot": [[99, 0, 0],
                                [0, -98, 17],
                                [0, -17, -98]],
                        "name": "pc5"},
                        "port": 52537}}}
"""


def main():
    controller = gl.getCurrentController()
    owner = controller.owner
    car = int(owner.name[-1:]) # example "car00" return 0
    if not owner["once"]:
        init(owner, car)
    if owner["once"]:
        run(owner, car)

def init(owner, car):
    owner["once"] = True
    standalone = False
    try:
        gl.master_init
    except:
        standalone = True
    if standalone:
        print("The car: car0{0} run standalone" . format(car))
        gl.carDict = {}
        gl.joystickOPY = Joystick()
        ini_file = gl.expandPath("//") + "car0" + str(car) + ".ini"
    else:
        print("The car: car0{0} run in BuggyGame" . format(car))
        ini_file = gl.expandPath("//cars/car0") + str(car) + "/car0" + str(car) + ".ini"

    print("Car config file =", ini_file)
    configDict = get_config_ini(ini_file)

    # Création de l'objet voiture
    # Get blender objects
    objDict = get_all_obj_in_dict()
    carOBL = objDict["car0" + str(car)]
    tire = [0, 0, 0, 0]
    for i in range(4):
        tire[i] = objDict["tire" + str(i) + "_0" + str(car)]
    # Création de la voiture
    gl.carDict[car] = Car(carOBL, tire, configDict)
    print("Python object car0{0} created in gl.carDict". format(car))

def run(owner, car):
    standalone = False
    try:
        gl.master_init
    except:
        standalone = True

    if standalone:
        run_standalone(car)
    else:
        run_in_game(car)

    # Update attributs
    gl.carDict[car].the_car_rolls()
    owner["vitesse"] = gl.carDict[car].vitesse

def run_standalone(car):
    # Joystick
    gl.joystickOPY.update()
    if gl.joystickOPY.J1: # joy_number est le nombre de joystick connecté
        j = gl.joystickOPY.J1.joyOut
        gl.carDict[car].mouvement_joystick(j[0], j[1], 500, 0.32)
    else:
        gl.carDict[car].mouvement_keyboard()

def run_in_game(car):
    mode = gl.playerTable[car]

    ## Reactivation d'une voiture cachée sous le terrain
    for i in range(4):
        if gl.reactive[i] == 1:
            print("Car0{} reactived car = {}".format(i, car))
            # Je remonte la voiture au dessus du terrain
            try:  # bug à la création des voitures pas grave
                if n == 0:
                    gl.carDict[i].set_position(-2, -3, 20)
                if n == 1:
                    gl.carDict[i].set_position(2, -9, 20)
                if n == 2:
                    gl.carDict[i].set_position(-2, -9, 20)
                if n == 3:
                    gl.carDict[i].set_position(3, -15, 20)
            except:
                pass
            gl.reactive[i] = 0

    ## Puissance: Valeur dans le dict créé dans master_init set_settings
    p = gl.settings[(car, "Power")]  # 500

    ## Masquage de accel pour tout, sauf wheel qui le modifie dans wheel mode
    objDict = get_all_obj_in_dict()
    objDict["accel0" + str(car)].localScale = [0, 1, 1]
    if car == 0:
        #if gl.rot != [0, 0, 0]:
        camera_rotation(objDict["camCar00"])

    ## Application de la table
    if mode == "J1":
        if gl.joystickOPY.J1:
            j = gl.joystickOPY.J1.joyOut
            gl.carDict[car].mouvement_joystick(j[0], j[1], p, 0.32)
    if mode == "J2":
        if gl.joystickOPY.J2:
            j = gl.joystickOPY.J2.joyOut
            gl.carDict[car].mouvement_joystick(j[0], j[1], p, 0.32)
    if mode == "A":
        gl.carDict[car].mouvement_keyboard()
    if mode == "Z":
        gl.carDict[car].mouvement_keyboard_ZQSD()
    if mode == -1:
        if car == 0:
            gl.carDict[car].set_position(-2, -3, -3)
        if car == 1:
            gl.carDict[car].set_position(2, -9, -3)
        if car == 2:
            gl.carDict[car].set_position(-2, -9, -3)
        if car == 3:
            gl.carDict[car].set_position(3, -15, -3)

    ## Dynamic Settings when running
    if mode == "W":
        sets = get_sets_wheel(car)
        p = sets["Power"]
        # Force et direction
        wheel_mode(car, p)
        # Suspension
        gl.carDict[car].set_suspension_settings(sets)
    else:
        # Suspension seule
        gl.carDict[car].set_suspension_settings(get_settings(car))

    ## Copie de position qui viennent du serveur
    if mode in [0, 1, 2, 3]:
        for val in gl.cars.values():
            pos = val["position"]
            if pos == mode:
                try:  # pas de data si jeu pas en cours
                    loc = val["car"]["loc"]  # gl.cars["loc"]
                    rot = val["car"]["rot"]
                    l, r = division_par_100(loc, rot)
                    gl.carDict[car].set_Loc_Rot(l, r)
                except:
                    pass

def lissage_rot():
    liss = [0, 0]

    for i in [0, 1]:
        nb = [50, 20][i]
        if len(gl.rot_liss[i]) < nb:
            gl.rot_liss[i].append(gl.rot[i])
        else:
            gl.rot_liss[i].append(gl.rot[i])
            gl.rot_liss[i].pop(0)
            s = [0, 0]
            for k in range(nb):
                s[i] += gl.rot_liss[i][k]
            liss[i] =  s[i] / nb

    #print(gl.rot, gl.rot_liss, liss)
    return liss

def camera_rotation(cam):  #, boussole):
    """Rotation de la camera de car00 avec le casque."""

    ## camera: l'axe vertical d'une caméra qui regarde horizontalement est y
    alpha = gl.rot[1]
    beta = -gl.rot[0]
    gamma = 0 #-gl.rot[1]

    # set objects orientation with alpha, beta, gamma in radians
    rot_en_euler_cam = mathutils.Euler([alpha, beta, gamma])
    # apply to objects local orientation if ok
    cam.localOrientation = rot_en_euler_cam.to_matrix()

    # objet boussole
    ##alpha_boussole = gl.rot[0]
    ##beta_boussole = 0  #gl.rot[1]
    ##gamma_boussole = gl.rot[2]
##
    ### set objects orientation with alpha, beta, gamma in radians
    ##rot_en_euler_boussole = mathutils.Euler([alpha_boussole,
                                            ##beta_boussole,
                                            ##gamma_boussole])
    ### apply to objects local orientation if ok
    ##boussole.localOrientation = rot_en_euler_boussole.to_matrix()

def division_par_100(loc, rot):
    """Fait ici avant application pour affichage des datas en terminal
    toujours en entiers
    de [-32, 1311, 94] [[99, -8, 0], [8, 99, 2], [0, -2, 99]]
    à [-0.32, 13,11, 0.94] [[0.99, -0.08, etc ... 0], [8, 99, 2], [0, -2, 99]]
    l'affichage est plus court et plus stable pour lecture."""
    k = loc[0] / 100
    l = loc[1] / 100
    m = loc[2] / 100
    l = [k, l, m]

    a = rot[0][0] / 100
    b = rot[0][1] / 100
    c = rot[0][2] / 100

    d = rot[1][0] / 100
    e = rot[1][1] / 100
    f = rot[1][2] / 100

    g = rot[2][0] / 100
    h = rot[2][1] / 100
    i = rot[2][2] / 100

    r = [[a, b ,c], [d, e, f], [g, h, i]]

    return l, r

def wheel_mode(car, p):
    """Correction de alpha avec la vitesse
        vitesse basse = angle fort
        vitesse haute = angle faible
        a, b = droiteAffine(x1, y1, x2, y2)
        à 100, angle ok
        diminution au dessus: 1 demi doite à droite
        augmentation en dessous: 1 demi droite à gauche
        continuité avec les 2 demi droite en (100, 1).

        p = puissance
        Applique la force et l'angle sur la voiture à la fin.
    """

    try:
        alpha0 = 1.3
        alpha1 = 0.7
        v1 = 100
        v2 = 200
        echelle = 800.0
        vitesse = gl.carDict[car].vitesse

        # à gauche
        if vitesse <= 100:
            a, b = droiteAffine(0, alpha0, v1, 1)
        # à droite
        if vitesse > 100:
            a, b = droiteAffine(100, 1, v2, alpha1)
        # correction en fonction de la vitesse de l'angle à faire
        cor = a * vitesse + b

        accy = gl.phone[0]
        # accy donne l'angle du volant, nouveau nom beta pour clarté !
        alpha = accy / echelle
        beta = alpha * cor

        # force
        accel = - gl.phone[1] / 100.0
        brake = gl.phone[2] / 100.0

        # Affichage de l'accélération
        objDict = get_all_obj_in_dict()
        # accel: 0 pour 0, 1 pour 1
        objDict["accel0" + str(car)].localScale = [-accel, 1, 1]

        # Limite
        if brake == 0:
            force = accel
        if accel == 0:
            force = brake
        if force > 1:
            force = 1
        if force < -1:
            force = -1

        # Application sur la voiture:      upDown, leftRight, power=600, direction=0.3
        gl.carDict[car].mouvement_joystick(force,  beta,      p,         0.32)
    except:
        print("Bug wheel mode")
        pass

def get_config_ini(ini_file):
    parser = ConfigParser()
    parser.read(ini_file)
    configDict = {}
    configDict["tirePos"] = json.loads(parser.get('tire', 'tirePos'))
    configDict["tireAxis"] = json.loads(parser.get('tire', 'tireAxis'))
    configDict["tireRadius"] = json.loads(parser.get('tire', 'tireRadius'))
    configDict["tireSteer"] = json.loads(parser.get('tire', 'tireSteer'))
    configDict["suspension_Angle"] = json.loads(parser.get('suspension', 'suspension_Angle'))
    configDict["suspensionHeight"] = json.loads(parser.get('suspension', 'suspensionHeight'))
    configDict["SuspComp"] = json.loads(parser.get('dynamics', 'SuspComp'))
    configDict["SuspDamp"] = json.loads(parser.get('dynamics', 'SuspDamp'))
    configDict["SuspStiff"] = json.loads(parser.get('dynamics', 'SuspStiff'))
    configDict["Roll"] = json.loads(parser.get('dynamics', 'Roll'))
    configDict["TyreFrict"] = json.loads(parser.get('dynamics', 'TyreFrict'))
    return configDict

def get_settings(car):
    settings = {}
    # Set Suspension Compression
    settings["SuspComp"] = gl.settings[(car, "SuspComp")]
    # Set Suspension Damping
    settings["SuspDamp"] = gl.settings[(car, "SuspDamp")]
    # Set Suspension Stiffness
    settings["SuspStiff"] = gl.settings[(car, "SuspStiff")]
    # Set Roll Influence
    settings["Roll"] = gl.settings[(car, "Roll")]
    # Set Tyre Friction
    settings["TyreFrict"] = gl.settings[(car, "TyreFrict")]
    return settings

def apply_sets_wheel(sets, k, ini_name, wheel_name, slider_obj):
    """Retourne le dict sets avec nouvelle clé de réglage et sa valeur
    modifiée par wheel
    Affiche le slider idoine à la bonne position.
    ini_name="SuspDamp", nominal=100,
    wheel_name="amortissement", slider_obj="D00"
    k = % de variation
    Power = 500
    Tyre Friction = 5.0
    Suspension Stiffness = 100.0
    Suspension Damping = 100.0
    Roll Influence = 0.05
    Suspension Compression = 10.0 sans slider
    """

    # Valeur dans le dict créé dans master_init set_settings
    settings_val = gl.settings[(0, ini_name)]
    wheel_slider = gl.tuning[wheel_name]
    sets[ini_name] = settings_val * (1 + k * ((wheel_slider- 50)/50))
    # Affichage du slider dans le HUD
    mini = settings_val * (1 - k)
    maxi = settings_val * (1 + k)
    # Les sliders bouge avec scale de 0.89 à 1.117
    s1 = 0.89
    s2 = 1.117
    a, b = droiteAffine(mini, s1, maxi, s2)
    # Equation de la droite
    D = a * sets[ini_name] + b
    # Application dans le HUD
    objDict = get_all_obj_in_dict()
    objDict[slider_obj].localScale = [D, D, 1]

    return sets

def get_sets_wheel(car):
    """gl.tuning = {"adherence": 50,
                    "amortissement": 50,
                    "puissance": 50,
                    "raideur": 50,
                    "roulis": 50}"""

    sets = {}

    # Set Suspension Compression sans slider
    sets["SuspComp"] = gl.settings[(car, "SuspComp")]

    # Set Power
    sets = apply_sets_wheel(sets, 0.3, "Power", "puissance", "P0" + str(car))

    # Set Tyre Friction
    sets = apply_sets_wheel(sets, 0.3, "TyreFrict", "adherence", "F0" + str(car))

    # Set Suspension Stiffness
    sets = apply_sets_wheel(sets, 0.3, "SuspStiff", "raideur", "S0" + str(car))

    # Set Suspension Damping
    sets = apply_sets_wheel(sets, 0.3, "SuspDamp", "amortissement", "D0" + str(car))

    # Set Roll Influence
    sets = apply_sets_wheel(sets, 0.2, "Roll", "roulis", "R0" + str(car))

    return sets

def get_all_obj_in_dict():
    # Get all blender objects from all scenes in a dict {object.name: object}
    scenes = gl.getSceneList()
    objDict = {}
    for scn in scenes:
        for obj in scn.objects:
            objDict[obj.name] = obj
    return objDict
