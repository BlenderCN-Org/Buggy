#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Documention sur arduino:

https://github.com/

Cette classe communique avec la carte Arduino,

retourne les angles pour la caméra du casque 3D.

La carte Arduino doit tourner avec le sketch MPU6050_DMP6.ino

"""

import sys
from time import sleep
import threading

try:
    import serial
except ImportError:
    print("Vous devez installer serial python3-serial")
    sys.exit()


class MPU6050():
    '''Gestion du socket avec carte Arduino, et la puce MPU6050
    calcule, retourne les angles pour la caméra Blender
    La carte Arduino doit tourner avec le sketch MPU6050_DMP6.ino
    '''

    def __init__(self, device, lissage):
        self.device = device
        self.loop = 1
        self.MPU_data = [0, 0, 0, 0, 0, 0, 0]
        self.cam_ori = [0,0,0]

        self.ori_queue = [[], [], []]

        self.lissage = lissage
        for i in [0, 1, 2]:
            self.ori_queue[i] = Lissage(lissage)

        self.arduino_socket = None
        #while not self.arduino_socket:
        self.arduino_init()

    def arduino_init(self):
        try:
            self.arduino_socket = serial.Serial(self.device, 9600)
            self.arduino_socket.timeout = 1
            print("\nInitialisation de la carte Arduino...")
            sleep(2)
            print("C'est fait\n")
        except :
            print("Pas de carte Arduino,")
            print("or you must add your user to dialout:")
            print("   sudo usermod -a -G dialout your_user")
            print("and restart\n")
        #sleep(10)

    def read_thread(self):
        if self.arduino_socket:
            thread10 = threading.Thread(target=self.read_loop)
            thread10.start()

    def read_loop(self):
        # envoi d'un caractère pour démarrer l'envoi sur l'arduino
        sleep(0.1)
        self.write("B")
        sleep(0.1)
        while self.loop:
            self.read()
            sleep(0.01)

    def read(self):
        if self.arduino_socket:
            try:
                data = self.arduino_socket.readline()
                self.decode(data)
            except:
                print("Pb at read()")
        else:
            print("Test sans carte Arduino")

    def decode(self, data):
        if data:
            try:
                l = data[:-2].decode("utf-8").split("t")
                if len(l) == 3:
                    # angles en degrés pour terminal
                    for i in range(3):
                        l[i] = int(float(l[i]))
                    # angles en radians pour blender
                    for i in range(3):
                        l[i] = l[i] * 3.14159/ 180
                        self.ori_queue[i].append(l[i])
                        self.ori_queue[i].average_calcul()

                    self.cam_ori  = [   self.ori_queue[0].average,
                                        self.ori_queue[1].average,
                                        self.ori_queue[2].average]
                    print(self.cam_ori)
            except:
                print("Erreur")

    def write(self, char):
        if self.arduino_socket:
            if char in ['B']:
                self.arduino_socket.write(str(char).encode())
            else:
                print(("{0} isn't in list of available characters".format(char)))
        else:
            print("Test without arduino card")

    def close(self):
        if self.arduino_socket:
            self.arduino_socket.close()
            print("Carte Arduino close")


class Lissage():
    """Queue pour faire moyenne des dernières valeurs."""

    def __init__(self, len_queue):
        self.queue = []
        self.len_queue = len_queue
        self.average = 0

    def append(self, new):
        self.queue.append(new)
        if len(self.queue) > self.len_queue:
            self.queue.pop(0)
        self.average_calcul()

    def average_calcul(self):
        somme = 0
        for i in range(len(self.queue)):
            somme += self.queue[i]
        if len(self.queue) == 0:
            self.average = 0
        else:
            self.average = somme / len(self.queue)


if __name__ == '__main__':
    device = "/dev/ttyUSB0"
    capt = MPU6050(device, 10)
    capt.read_loop()
    capt.close()
