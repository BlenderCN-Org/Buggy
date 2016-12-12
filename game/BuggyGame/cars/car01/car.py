#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## car.py

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
from bge import constraints
from bge import events

class Car():
    ''' car = car object in blender
        Only with 4 wheels
        tire = list of 4 tires objects in blender
        tire or tyre = in french pneu,
                        the entire wheel must be the blender object
                        or the rim(jante) must be parented to tire !

    '''
    def __init__(self, car, tire, car_config):
        self.tireOBL = tire
        self.car_config = car_config
        # or create an instance with gl.car = Car(car, tire, 0)
        # and uncomment the below line
        #self.car_config = default_car_settings()
        self.carOBL = car
        self.vitesse = 0
        self.Loc_Rot = []

        # Set Physics
        self.physics_id = self.carOBL.getPhysicsId()
        # create a vehicle constraint
        self.constraint = constraints.createConstraint(self.physics_id, 0, 11)
        # get the constraint ID
        self.constraint_ID = self.constraint.getConstraintId()
        # get the vehicle constraint ID
        self.vehicle = constraints.getVehicleConstraint(self.constraint_ID)

        # Add tire
        for i in range(4):
            self.vehicle.addWheel(self.tireOBL[i],
                                self.car_config["tirePos"][i],
                                self.car_config["suspension_Angle"],
                                self.car_config["tireAxis"],
                                self.car_config["suspensionHeight"][i],
                                self.car_config["tireRadius"][i],
                                self.car_config["tireSteer"][i])

        apply_suspension(self.vehicle, self.car_config)

    def set_suspension_settings(self, car_config):
        apply_suspension(self.vehicle, car_config)

    def mouvement_keyboard(self):
        power = 0
        UP_status = gl.keyboard.events[events.UPARROWKEY]
        if UP_status == gl.KX_INPUT_ACTIVE:
            power = -500
        DOWN_status = gl.keyboard.events[events.DOWNARROWKEY]
        if DOWN_status == gl.KX_INPUT_ACTIVE:
            power = 500
        # Apply power to all four tires
        for i in range(4):
            self.vehicle.applyEngineForce(power, i)
        direction = 0
        LEFT_status = gl.keyboard.events[events.LEFTARROWKEY]
        if LEFT_status == gl.KX_INPUT_ACTIVE:
            direction = 0.2 - self.vitesse/1000
        RIGHT_status = gl.keyboard.events[events.RIGHTARROWKEY]
        if RIGHT_status == gl.KX_INPUT_ACTIVE:
            direction = -0.2 - self.vitesse/1000
        # Turn with Front Tire
        for i in range(2):
            self.vehicle.setSteeringValue(direction, i)

    def mouvement_keyboard_ZQSD(self):
        power = 0
        Z_status = gl.keyboard.events[events.ZKEY]
        if Z_status == gl.KX_INPUT_ACTIVE:
            power = -500
        S_status = gl.keyboard.events[events.SKEY]
        if S_status == gl.KX_INPUT_ACTIVE:
            power = 500
        # Apply power to all four tires
        for i in range(4):
            self.vehicle.applyEngineForce(power, i)
        direction = 0
        Q_status = gl.keyboard.events[events.QKEY]
        if Q_status == gl.KX_INPUT_ACTIVE:
            direction = 0.2 - self.vitesse/1000
        D_status = gl.keyboard.events[events.DKEY]
        if D_status == gl.KX_INPUT_ACTIVE:
            direction = -0.2 - self.vitesse/1000
        # Turn with Front Tire
        for i in range(2):
            self.vehicle.setSteeringValue(direction, i)

    def mouvement_joystick(self, upDown, leftRight, power=600, direction=0.3):
        p = power * upDown # power de -500 à 500, upDown de -1 à 1
        # Apply power to all four tires
        for i in range(4):
            self.vehicle.applyEngineForce(p, i)

        # Turn
        # Régler ces 2 valeurs, pas ailleurs
        # TODO mettre ça dans le ini
        A = 0.7
        B = 0.002
        V1 = 50
        V2 = 240

        a, b = droiteAffine(V1, A, V2, B)

        if self.vitesse <= V1:
            c = A

        if V1 < self.vitesse < V2:
            c = a * self.vitesse + b

        if self.vitesse >= V2:
            c = B

        d = - direction * c * leftRight

        # Turn with Front Tire
        for i in range(2):
            self.vehicle.setSteeringValue(d, i)

        # Apply Suspension settings always
        name = self.carOBL.name # car00
        c = int(name[-1:]) # 0 to 3
        simpleDict = {}
        simpleDict["SuspComp"] = gl.settings[(c, "SuspComp")]
        simpleDict["SuspDamp"] = gl.settings[(c, "SuspDamp")]
        simpleDict["SuspStiff"] = gl.settings[(c, "SuspStiff")]
        simpleDict["Roll"] = gl.settings[(c, "Roll")]
        simpleDict["TyreFrict"] = gl.settings[(c, "TyreFrict")]
        apply_suspension(self.vehicle, simpleDict)

    def motor_sound(self, upDown):
        vitesse = self.vitesse
        gasPedal = abs(upDown)
        pitchMin = 1.0
        pitchMax = 2.0
        volume, pitch = 0, 0

        # Pitch fonction de la vitesse
        if vitesse < 3 :
            a , b = droiteAffine(0, 0.5, 1, pitchMax)
            pitch = a * gasPedal + b # équivaut à débrayé ou point mort
        if vitesse >= 3 and vitesse < 20 :
            a , b = droiteAffine(0, pitchMin*1.1, 19, pitchMax)
            pitch = a * vitesse + b
        if vitesse >= 20 and vitesse < 50 :
            a , b = droiteAffine(20, pitchMin*1.2, 49, pitchMax)
            pitch = a * vitesse + b
        if vitesse >= 50 and vitesse < 90 :
            a , b = droiteAffine(50, pitchMin*1.4, 89, pitchMax*1.2)
            pitch = a * vitesse + b
        if vitesse >= 90 and vitesse < 140 :
            a , b = droiteAffine(90, pitchMin*1.6, 139, pitchMax*1.2)
            pitch = a * vitesse + b
        if vitesse >= 140:
            a , b = droiteAffine(140, pitchMin*1.8, 199, pitchMax*1.2)
            pitch = a * vitesse + b


        ## Volume fonction du pitch, des gaz, de la vitesse

        # Volume = f(pitch)
        # de pitchMin à pitchMax soit 0.5 à 2.5
        # en x: pitch 0.5 à 2.5, en y: vol_pitch 0.2 à 1
        a, b = droiteAffine(0.5, 0.2, 2.5, 1)
        vol_pitch = a * pitch + b

        # Volume = f(gasPedal)
        # en x: gasPedal 0 à 1, en y: vol_gas 0.5 à 1
        a, b = droiteAffine(0, 0.1, 1, 1)
        vol_gas =  a * gasPedal  + b

        # Volume = f(vitesse)
        # en x: vitesse 0 à 200, en y: vol_vit 0.5 à 1
        a, b = droiteAffine(0, 0.5, 200, 1)
        vol_vit = a * vitesse + b

        # Volume de 0.5*0.5*0.5=0.12  à  2.5*1*1=2.5
        volume = 0.3*vol_vit + 0.4*vol_gas + 0.3*vol_pitch

        return volume, pitch

    def the_car_rolls(self):
        # get local (game object) linear velocity
        v = self.carOBL.getLinearVelocity(True)
        # Realistic speed
        self.vitesse = 5 * (v[0]**2 + v[1]**2 + v[2]**2) ** 0.5
        # Loc Rot
        l = self.carOBL.position # liste de 3
        r = self.carOBL.orientation # liste de 3 listes de 3
        self.Loc_Rot = l, r

    def set_position(self, x, y, z):
        self.carOBL.worldPosition = [x, y, z]
        self.carOBL.worldOrientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def set_Loc_Rot(self, loc, rot):
        self.carOBL.worldPosition = loc
        self.carOBL.worldOrientation = rot


def apply_suspension(vehicle, car_config):
    for i in range(4):
        vehicle.setSuspensionCompression(car_config["SuspComp"], i)
        vehicle.setSuspensionDamping(car_config["SuspDamp"], i)
        vehicle.setSuspensionStiffness(car_config["SuspStiff"], i)
        vehicle.setRollInfluence(car_config["Roll"], i)
        vehicle.setTyreFriction(car_config["TyreFrict"], i)

def droiteAffine(x1, y1, x2, y2):
    ''' Return a, b in y = ax + b
    with 2 points (x1,y1) et (x2,y2) '''
    a = (y2 - y1) / (x2 - x1)
    b = y1 - (a * x1)
    return a, b

def default_car_settings():
    ''' This fonction create a default dict without car.ini
        and return this dict '''
    car_config = {}
    # Front driver tire position from car object center
    car_config["tirePos"] = [[ -1.0,  1.4, -0.5],
                            [1.0,  1.4, -0.5],
                            [-1.0, -0.9, -0.4],
                            [1.0,  -0.9, -0.4]]

    # tire axis attached to car axle
    car_config["tireAxis"] = [-1.0, 0.0, 0.0]
    # set tire radius
    car_config["tireRadius"] = [0.38, 0.38, 0.4, 0.4]
    # Tire has steering ?
    car_config["tireSteer"] = [1, 1, 0, 0]

    # suspension angle from car object center
    car_config["suspension_Angle"] = [0.0, 0.0, -1.0]
    # set suspension height
    car_config["suspensionHeight"] = [0.2, 0.2, 0.35, 0.35]

    # Settings with car = 200 kg
    # Set Suspension Compression
    car_config["SuspComp"] = 10.0
    # Set Suspension Damping
    car_config["SuspDamp"] = 100.0
    # Set Suspension Stiffness
    car_config["SuspStiff"] = 100.0
    # Set Roll Influence
    car_config["Roll"] = 0.05
    # Set Tyre Friction
    car_config["TyreFrict"] = 2.0

    return car_config
