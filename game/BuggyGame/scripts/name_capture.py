#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## name_capture.py

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
from time import time

controller = gl.getCurrentController()
owner = controller.owner

if not owner['end']:
    # Get your name in Text prop
    my_name = owner['yourName']

    # delete \n = Return
    gl.my_name = my_name.rstrip()

    # default
    if gl.my_name == 0:
        gl.my_name = time()

    gl.globalDict["my_name"] = gl.my_name
    print("Mon nom est: ", gl.my_name)

    gl.globalDict["players"][gl.my_name] = [99999, 99999, 99999, 99999, 99999, 0]
    gl.saveGlobalDict()
