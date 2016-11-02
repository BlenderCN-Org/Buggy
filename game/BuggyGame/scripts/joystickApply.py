#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## joystickApply.py

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

def joysticks_invert(objDict):
    scenes = gl.getSceneList()
    for scn in scenes:
        if scn.name == "Menu":
            if objDict["m1"]["enable"]:
                if gl.joystickOPY.J1:
                    if objDict["invert_sticks"]["enable"]:
                        gl.joystickOPY.J1.invert_sticks = True
                    else:
                        gl.joystickOPY.J1.invert_sticks = False

                    if objDict["invert_LeftRight"]["enable"]:
                        gl.joystickOPY.J1.invert_LeftRight = True
                    else:
                        gl.joystickOPY.J1.invert_LeftRight = False

                    if objDict["invert_UpDown"]["enable"]:
                        gl.joystickOPY.J1.invert_UpDown = True
                    else:
                        gl.joystickOPY.J1.invert_UpDown = False

                    if objDict["invert_LR__to_UD"]["enable"]:
                        gl.joystickOPY.J1.invert_LR__to_UD = True
                    else:
                        gl.joystickOPY.J1.invert_LR__to_UD = False

                    if objDict["invert_UD__to_LR"]["enable"]:
                        gl.joystickOPY.J1.invert_UD__to_LR = True
                    else:
                        gl.joystickOPY.J1.invert_UD__to_LR = False

            if objDict["m2"]["enable"]:
                if gl.joystickOPY.J2:
                    if objDict["invert_sticks"]["enable"]:
                        gl.joystickOPY.J2.invert_sticks = True
                    else:
                        gl.joystickOPY.J2.invert_sticks = False

                    if objDict["invert_LeftRight"]["enable"]:
                        gl.joystickOPY.J2.invert_LeftRight = True
                    else:
                        gl.joystickOPY.J2.invert_LeftRight = False

                    if objDict["invert_UpDown"]["enable"]:
                        gl.joystickOPY.J2.invert_UpDown = True
                    else:
                        gl.joystickOPY.J2.invert_UpDown = False

                    if objDict["invert_LR__to_UD"]["enable"]:
                        gl.joystickOPY.J2.invert_LR__to_UD = True
                    else:
                        gl.joystickOPY.J2.invert_LR__to_UD = False

                    if objDict["invert_UD__to_LR"]["enable"]:
                        gl.joystickOPY.J2.invert_UD__to_LR = True
                    else:
                        gl.joystickOPY.J2.invert_UD__to_LR = False

def joysticks_test_Menu(objDict):
    scenes = gl.getSceneList()
    for scn in scenes:
        if scn.name == "Menu":
            if gl.joystickOPY.J1 and objDict["m1"]["enable"]:
                JJ = gl.joystickOPY.J1
                c = "00"
                apply_joysticks_test_Menu(objDict, JJ, c)
            if gl.joystickOPY.J2 and objDict["m2"]["enable"]:
                JJ = gl.joystickOPY.J2
                c = "01"
                apply_joysticks_test_Menu(objDict, JJ, c)

def apply_joysticks_test_Menu(objDict, JJ, c):
    # JJ = gl.joystickOPY.J1 and c = "00"
    # Stick
    t = 0.5 + JJ.joyOut[1]/2
    objDict["turn"].localScale = [t, 1, 1]

    a = 0.5 - JJ.joyOut[0]/2
    objDict["acc"].localScale = [1, 1, a]

    # Buttons D S R F P scale 0 to 2 with JJ.coeff[i] -10 to 10
    D = 1 + JJ.coeff[4]/10
    objDict["SuspDamp"].localScale = [D, 1, 1]
    gl.settings[(c, "SuspDamp")] = 100 + 30 * (D - 1)

    S = 1 + JJ.coeff[2]/10
    objDict["SuspStiff"].localScale = [S, 1, 1]
    gl.settings[(c, "SuspStiff")] = 100 + 30 * (S - 1)

    R = 1 + JJ.coeff[3]/10
    objDict["Roll"].localScale = [R, 1, 1]
    gl.settings[(c, "Roll")] = 0.05 + 0.0015 * (R - 1)

    F = 1 + JJ.coeff[1]/10
    objDict["TyreFrict"].localScale = [F, 1, 1]
    gl.settings[(c, "TyreFrict")] = 2 + 0.18 * (F - 1)

    P = 1 + JJ.coeff[0]/10
    objDict["Power"].localScale = [P, 1, 1]
    gl.settings[(c, "Power")] = 500 + 300 * (P - 1)

def joysticks_Race(objDict):
    scenes = gl.getSceneList()
    for scn in scenes:
        if "Race" in scn.name:
            if gl.joystickOPY.J1:
                JJ = gl.joystickOPY.J1
                # Buttons D S R F P scale 0 to 2 with gl.joystickOPY.J1.coeff[i] -10 to 10
                D = 1 + JJ.coeff[4]/10
                objDict["D00"].localScale = [D, D, 1]
                gl.settings[("00", "SuspDamp")] = 100 + 30 * (D - 1)

                S = 1 + JJ.coeff[2]/10
                objDict["S00"].localScale = [S, S, 1]
                gl.settings[("00", "SuspStiff")] = 100 + 30 * (S - 1)

                R = 1 + JJ.coeff[3]/10
                objDict["R00"].localScale = [R, R, 1]
                gl.settings[("00", "Roll")] = 0.05 + 0.0015 * (R - 1)

                F = 1 + JJ.coeff[1]/10
                objDict["F00"].localScale = [F, F, 1]
                gl.settings[("00", "TyreFrict")] = 2 + 0.18 * (F - 1)

                P = 1 + JJ.coeff[0]/10
                objDict["P00"].localScale = [P, P, 1]
                gl.settings[("00", "Power")] = 500 + 300 * (P - 1)

            if gl.joystickOPY.J2:
                JJ = gl.joystickOPY.J2
                # Buttons D S R F P scale 0 to 2 with gl.joystickOPY.J1.coeff[i] -10 to 10
                D = 1 + JJ.coeff[4]/10
                objDict["D01"].localScale = [D, D, 1]
                gl.settings[("01", "SuspDamp")] = 100 + 30 * (D - 1)

                S = 1 + JJ.coeff[2]/10
                objDict["S01"].localScale = [S, S, 1]
                gl.settings[("01", "SuspStiff")] = 100 + 30 * (S - 1)

                R = 1 + JJ.coeff[3]/10
                objDict["R01"].localScale = [R, R, 1]
                gl.settings[("01", "Roll")] = 0.05 + 0.0015 * (R - 1)

                F = 1 + JJ.coeff[1]/10
                objDict["F01"].localScale = [F, F, 1]
                gl.settings[("01", "TyreFrict")] = 2 + 0.18 * (F - 1)

                P = 1 + JJ.coeff[0]/10
                objDict["P01"].localScale = [P, P, 1]
                gl.settings[("01", "Power")] = 500 + 300 * (P - 1)
