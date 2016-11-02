#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Documention sur arduino:

https://github.com/

Cette classe communique avec la carte Arduino,

retourne les angles pour la caméra du casque 3D.

"""

import sys
from math import sin, cos, atan, asin
from time import sleep
import threading

try:
    import serial
except ImportError:
    print("Vous devez installer serial python3-serial")
    sys.exit()


class MPU6050():
    '''Gestion du socket avec carte Arduino, et la puce MPU6050
    calcule, retourne les angles pour la caméra Blender'''

    def __init__(self, device):
        self.device = device
        self.loop = 1
        self.MPU_data = [0, 0, 0, 0, 0, 0, 0]
        self.cam_ori = [0,0,0]

        self.arduino_socket = None
        while not self.arduino_socket:
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
        sleep(3)

    def read_thread(self):
        thread10 = threading.Thread(target=self.read_loop)
        thread10.start()

    def read_loop(self):
        # envoi d'un caractère pour démarrer l'envoi sur l'arduino
        self.write("B")
        while self.loop:
            self.read()
            sleep(0.100)

    def read(self):
        if self.arduino_socket:
            #data = self.arduino_socket.read()
            data = self.arduino_socket.readline()
            self.decode(data)
        else:
            print("Test sans carte Arduino")

    def decode(self, data):
        if data:
            l = ["No data"]
            try:
                # suppression des eof \n et \r, decode, découpe sur \
                l = data[:-2].decode("utf-8").split("t")
                if len(l) == 6:
                    print(l)
                ##values = []
                ##if len(l) == 7:
                    ##values.append(float(l[0]))
                    ##for i in range(6):
                        ### conversion de bytes à entier
                        ##values.append(int(l[i+1]))
                    ### je les prends si format ok
                    ##self.MPU_data = values
                    ##print(self.MPU_data[6])
                    ### ensuite intégration
                    ### TODO
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


if __name__ == '__main__':
    device = "/dev/ttyACM0"
    capt = MPU6050(device)
    capt.read_loop()
    capt.close()
