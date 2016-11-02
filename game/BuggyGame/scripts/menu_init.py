1#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## menu_init.py

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
from scripts.menu import Menu

def main():
    ''' dict with key = blender obj, value = link
        if link = integer, link = cam position with frame, if -1 no link (brick)
        never string in link !! '''
    obj_link = {"1j" : ("gl.number_of_players", 1),
                "2j" : ("gl.number_of_players", 2),
                "3j" : ("gl.number_of_players", 3),
                "4j" : ("gl.number_of_players", 4),
                "Jouer" : ("gl.play", 1),
                "Manettes" : (2, 0),
                "Aide" : (3, 0),
                "Credits" : (4, 0),
                "Retour.000" : (1, 0),
                "Retour.001" : (1, 0),
                "Retour.002" : (1, 0)}

    if gl.server:
        gl.menu = Menu(obj_link, "camMenu", frame=1, deltaL=2.5)
    else:
        gl.menu = Menu(obj_link, "camMenu", frame=5, deltaL=2.5)
