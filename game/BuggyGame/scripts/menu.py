#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## menu.py

#############################################################################
# Copyright (C) Labomedia March 2011
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

from time import time
from bge import logic as gl
from bge import events


class MenuFactory():
    ''' Generic class to manage a menu
        - Scale unscale with mouse over unover (set with object prop over)
        - Clic if over and left clic
        - Block during 1 second if clic for anover clic
        - Navigation with camera position set with frame property in Camera Action'''

    def __init__(self, obj, link, deltaL):
        ''' obj = Blender object
            link: if clic and integer, set cam frame, if -1 do nothing
            deltaL = grab on z coeff '''
        self.obj = obj
        self.deltaL = deltaL
        self.link = link
        self.moved = 1

    def move_and_link(self, frame, menu_block, menu_tempo):
        ''' Go to link if left clic
            Scale Blender Object if mouse over object '''
        # Scale
        if self.obj["over"] and self.moved == 1:
            self.moved = self.deltaL
            p = self.obj.worldPosition
            self.obj.worldPosition = [p[0], p[1], p[2] - 2.5]

        # Unscale
        if not self.obj["over"] and self.moved != 1:
            self.moved = 1
            r = self.obj.worldPosition
            self.obj.worldPosition = [r[0], r[1], r[2] + 2.5]

        # Link
        if menu_block == 0:
            if self.obj["clic"]:
                menu_block = 1
                menu_tempo = time()
                if isinstance(self.link[0], int):
                    frame = self.link[0]
                else:
                    exec(self.link[0] + "=" + str(self.link[1]))
                    if self.link[0] == "gl.number_of_players":
                        frame = 1
                # Dans tous les cas je force à False car True a été vu avant
                if self.obj["clic"] == True:
                    self.obj["clic"] = False
        return frame, menu_block, menu_tempo

class Menu(dict):
    ''' Example
    obj_link = {"1" : (gl.level, 1),
                "1j" : (gl.number_of_players, 1),
                "Valider.000" : (1, 0),
                "HitParade": "hitParade"} with "hitParade" = camera prop in Menu Scene
    dict with key = blender obj, value = (a, b)
    if a = integer: a = cam position with frame in prop, Action Actuator with frame property
    else: a = variable, set variable to b
'''

    def __init__(self, obj_link,  cam, frame, deltaL):
        self.obj_link = obj_link
        self.deltaL = deltaL
        # Get Blender obj with name in obj_link
        scene = gl.getCurrentScene()
        objList = scene.objects
        self.cam = objList[cam]
        self.frame = frame # First screen = choose number of players
        self.menu_block = 0
        self.menu_tempo = time()

        for obj, link in self.obj_link.items():
            try:
                # self.obj est l'objet Blender
                objBL = objList[obj]
                self[obj] = MenuFactory(objBL, link, deltaL)
            except:
                print("\n Blender Object ", obj, "doesn't exist")
                print("So you must update obj_link \n")

    def move_and_link_all(self):
        for key in self.obj_link.keys():
            self.frame, self.menu_block, self.menu_tempo = self[key].move_and_link(self.frame,
                                                                self.menu_block, self.menu_tempo)
        self.cam["frame"] = self.frame

        clic_STATUS = gl.mouse.events[events.LEFTMOUSE]
        if clic_STATUS == gl.KX_INPUT_NONE:
            clic = False
        else:
            clic = True
        # Block or unblock
        if time() - self.menu_tempo > 1:
            if clic == False:
                self.menu_block = 0
                self.menu_tempo = time()
