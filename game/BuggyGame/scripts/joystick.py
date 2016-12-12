#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## joystick.py

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


'''
Détecte si des joysticks sont connectés
Retourne en attribut:
- le nomdre d'axes 2 ou 4 (1 ou 2 proportionnels)
- les valeurs des 2 ou 4 axes: float de -1 à 1
- la valeur des boutons: liste avec numéro des boutons actionnés [2,10]

self.connected = True si au moins une manette est connectée
self.index       = liste des index existants ex [0, 1]
self.axis_number = 2 ou 4
self.buttons = liste de 0 à 10 indice, de valeurs 0 à 10 ex [0] ou [2,10]
self.upDown = 0.0    : de -1.0 à 1.0
self.letfRight = 0.0 : de -1.0 à 1.0
'''


from bge import logic as gl


class JoystickFactory():
    def __init__(self, index):
        self.index = index
        self.axis_number = gl.joysticks[self.index].numAxis
        self.buttons = 0
        self.upDown = 0
        self.letfRight = 0
        self.joyOut = [0, 0, 0]

        self.invert_sticks = False
        self.invert_UpDown = False
        self.invert_LR__to_UD = False
        self.invert_LeftRight = False
        self.invert_UD__to_LR = False

        self.coeff = [0, 0, 0, 0, 0] # 5 coeff with 10 buttons
        #                       coeff       add block
        # If apply I block, unblock if not in list
        self.coeffTable = { 0: ["self.coeff[0]", "-1", False],
                            3: ["self.coeff[0]",  "1", False],
                            1: ["self.coeff[1]", "-1", False],
                            2: ["self.coeff[1]",  "1", False],
                            4: ["self.coeff[2]", "-1", False],
                            6: ["self.coeff[2]",  "1", False],
                            5: ["self.coeff[3]", "-1", False],
                            7: ["self.coeff[3]",  "1", False],
                            8: ["self.coeff[4]", "-1", False],
                            9: ["self.coeff[4]",  "1", False],
                            }
        print("Joystick n°{0}".format(self.index))
        print("Nombre d'axes = {0}".format(self.axis_number))

    def update(self):
        self.buttons = gl.joysticks[self.index].activeButtons

        self.coeff_with_buttons_update()

        if self.axis_number == 4:
            self.update_4()
        elif self.axis_number == 6:
            self.update_xbox()
        else:
            print("Joystick class only with 4 or 6 axes")

    def update_4(self):
            # Invert axes
            if not self.invert_UD__to_LR:
                self.letfRight = gl.joysticks[self.index].axisValues[0]
            else:
                self.letfRight = - gl.joysticks[self.index].axisValues[1]
            if not self.invert_LR__to_UD:
                self.upDown = gl.joysticks[self.index].axisValues[2]
            else:
                self.upDown = - gl.joysticks[self.index].axisValues[3]

            # Invert sens
            if self.invert_LeftRight:
                self.upDown = - self.upDown
            if self.invert_UpDown:
                self.letfRight = - self.letfRight

            # Invert sticks
            if not self.invert_sticks:
                self.joyOut = [self.upDown, self.letfRight, self.buttons]
            else:
                self.joyOut = [self.letfRight, self.upDown, self.buttons]

    def update_xbox(self):
            # Invert axes
            if not self.invert_UD__to_LR:
                self.letfRight = gl.joysticks[self.index].axisValues[0]
            else:
                self.letfRight = - gl.joysticks[self.index].axisValues[1]

            if not self.invert_LR__to_UD:
                self.upDown = gl.joysticks[self.index].axisValues[3]
            else:
                self.upDown = - gl.joysticks[self.index].axisValues[5]


            # Invert sens
            if self.invert_LeftRight:
                self.upDown = - self.upDown
            if self.invert_UpDown:
                self.letfRight = - self.letfRight

            # Invert sticks
            if not self.invert_sticks:
                self.joyOut = [self.upDown, self.letfRight, self.buttons]
            else:
                self.joyOut = [self.letfRight, self.upDown, self.buttons]


    def coeff_with_buttons_update(self):
        bt = self.buttons
        for i in range(10):
            if i in bt:
                if not self.coeffTable[i][2]:
                    action = self.coeffTable[i]
                    exec(action[0] + "+="+ action[1])
                    # Block
                    self.coeffTable[i][2] = True
            else:
                # Unblock
                self.coeffTable[i][2] = False

        # All coeff beetwin -10 and 10
        for j in range(5):
            if self.coeff[j] > 10.0:
                self.coeff[j] = 10.0
            if self.coeff[j] < -10.0:
                self.coeff[j] = -10.0


class Joystick(list):
    def __init__(self):
        self.joy_number = 0
        self.J1 = None
        self.J2 = None
        for joy in gl.joysticks:
            if joy:
                self.joy_number += 1
                self.append(JoystickFactory(gl.joysticks.index(joy)))
        self.attribution()

    def update(self):
        for i in range(self.joy_number):
            self[i].update()

    def attribution(self):
        ''' Use joyOPY.J1.joyOut to get a list of output if not None
        and Use joyOPY.J2.joyOut if not None
            Only with maxi 2 joysticks
        '''

        if self.joy_number > 0:
            self.J1 = self[0]
            print("Joystick J1 {0} created".format(self.J1))
            if self.joy_number == 2:
                self.J2 = self[1]
                print("Joystick J2 {0} created".format(self.J2))
