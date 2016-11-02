#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Documention sur LSM303 arduino:

https://github.com/pololu/lsm303-arduino

Cette classe communique avec la carte Arduino,
corrige le compas avec la gravité,
retourne les angles pour la caméra du casque 3D.

Détails des calculs à
https://www.pololu.com/file/download/LSM303DLH-compass-app-note.pdf?file_id=0J434
soit
http://urlz.fr/2twv
"""

import sys
from math import sin, cos, atan, asin
from time import time, sleep
import threading

try:
    import serial
except ImportError:
    print("Vous devez installer serial python3-serial")
    sys.exit()


class LSM303():
    """Gestion du socket avec carte Arduino, et la puce LSM303
    calcule, retourne les angles pour la caméra Blender."""

    def __init__(self, device, lissage):
        """
        device = "/dev/ttyACM0"
        lissage = 20 = nombre de valeur pour calcul de la moyenne mobile.
        """
        self.device = device
        self.loop = 1
        self.LSM_data = [0, 0, 0, 0, 0, 0]
        self.gravite_queue = [[], []]

        self.lissage = lissage
        if self.lissage > 0:
            self.on_lissage = 1
        else:
            self.on_lissage = 0
        for i in [0, 1]:
            self.gravite_queue[i] = Lissage(lissage)

        self.cam_ori = [0, 0, 0]
        self.arduino_socket = None
        while not self.arduino_socket:
            self.arduino_init()
        self.t_0 = time()

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
        while self.loop:
            self.read()
            sleep(0.01)

    def read(self):
        if self.arduino_socket:
            data = self.arduino_socket.readline()
            self.decode(data)
            for i in [0, 1]:
                self.gravite_queue[i].append(self.LSM_data[i])
            self.cam_angle_calcul()
        else:
            print("Test sans carte Arduino")

    def decode(self, data):
        # suppression des eof \n et \r
        msg = data[:-2]
        # recup des 3*acc et 3*boussole
        try:
            # découpe du string en liste
            l = msg.split()
            values = [0, 0, 0, 0, 0, 0]
            for i in range(len(l)):
                # conversion de bytes à entier
                values[i] = int(l[i].decode("utf-8"))
            if len(values) == 6:
                self.LSM_data = values
        except:
            print("Pas de data reçues ou mal formatées ")

    def close(self):
        if self.arduino_socket:
            self.arduino_socket.close()
            print("Carte Arduino close")

    def cam_angle_calcul(self):
        """Défini les angles de la caméra en radians,
        imprime les angles en degrés.
        """

        # Valeurs brutes de magnétisme
        Mx1 = self.LSM_data[3]
        My1 = self.LSM_data[4]
        Mz1 = self.LSM_data[5]

        k_inf_1 = 14000 #16500
        rho, gamma = self.equation_10(k_inf_1)

        Mx2, My2 = self.equation_12(Mx1, My1, Mz1, rho, gamma)

        psi = self.equation_13(Mx2, My2)

        # psi, rho, gamma en radians
        #self.angle_degree_print(rho, gamma, psi)
        self.cam_ori = [rho, gamma, psi]
        #print(self.LSM_data[0], self.gravite_queue[0].average)

    def equation_10(self, k_inf_1):
        """Retourne rho, gamma = angle de compas sur x et y
        calculé avec la gravité, donc projeté sur un plan horizontal.

        Avec valeurs de gravité (accélération):
            - sans lissage, self.LSM_data[i]
            - avec lissage, self.gravite_queue[i].average

        """
        rho, gamma = 0, 0

        # Sans lissage
        if not self.lissage:
            if self.LSM_data[2] >= 0:
                raw_ax = self.LSM_data[0] / k_inf_1
                raw_ay = self.LSM_data[1] / k_inf_1
            if self.LSM_data[2] < 0:
                raw_ax = -self.LSM_data[0] / k_inf_1
                raw_ay = -self.LSM_data[1] / k_inf_1

        # Avec lissage
        else:
            if self.LSM_data[2] >= 0:
                raw_ax = self.gravite_queue[0].average / k_inf_1
                raw_ay = self.gravite_queue[1].average / k_inf_1
            if self.LSM_data[2] < 0:
                raw_ax = -self.gravite_queue[0].average / k_inf_1
                raw_ay = -self.gravite_queue[1].average / k_inf_1

        if raw_ax >= -1 and raw_ax <= 1:
            # rho compris entre - pi/2 et pi/2 soit plage de pi
            rho = asin(-raw_ax)
        else:
            rho = 0

        if cos(rho) != 0:
            if raw_ay / cos(rho) >= -1 and raw_ay / cos(rho) <= 1:
                # gamma compris entre - pi/2 et pi/2 soit plage de pi
                gamma = asin(raw_ay / cos(rho))
            else:
                gamma = 0
        else:
            gamma = 0

        return rho, gamma

    def equation_12(self, Mx1, My1, Mz1, rho, gamma):
        """Retourne les coordonnées du compas corrigé avec la gravité.

        Mz2 n'est pas utilisé
        Mz2 = - Mx1*cos(gamma)*sin(rho)+My1*sin(gamma)+Mz1*cos(gamma)*cos(rho)
        """

        Mx2 = Mx1*cos(rho) + Mz1*sin(rho)
        My2 = Mx1*sin(gamma)*sin(rho) + My1*cos(gamma) - Mz1*sin(gamma)*cos(rho)

        return Mx2, My2  #, Mz2

    def equation_13(self, Mx2, My2):
        """Retourne psi, calculé avec les axes x y du compas de l'équation 12."""
        psi = 0
        if Mx2 != 0:
            rap = My2/Mx2
        else:
            rap = 1

        angle_rad = atan(rap)

        if Mx2 > 0 and My2 > 0:
            psi = angle_rad  # rad
        if Mx2 < 0:
            psi = 3.14159 + angle_rad
        if Mx2 > 0 and My2 <= 0:
            psi = 2*3.14159 + angle_rad
        if Mx2 == 0 and My2 < 0:
            psi = 3.14159/2
        if Mx2 == 0 and My2 > 0:
            psi = 3 * 3.14159/2

        return psi

    def angle_degree_print(self, rho, gamma, psi):
        # pour terminal
        rho_deg = int(rho * 180 / 3.14159)
        gamma_deg = int(gamma * 180 / 3.14159)
        psi_deg = int(psi * 180 / 3.14159)
        t = time()
        if t - self.t_0 > 1:
            self.t_0 = t
            print(rho_deg, gamma_deg, psi_deg)


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
    device = "/dev/ttyACM2"
    lissage = 5
    capt = LSM303(device, lissage)
    capt.read_loop()
    capt.close()
