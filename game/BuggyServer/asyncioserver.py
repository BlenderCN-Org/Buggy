#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# asyncioserver.py

#############################################################################
# Copyright (C) Labomedia 2011:2015
#
#    This file is part of Buggy.
#
#    Buggy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Buggy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################

"""
UDP LAN server with asyncio
Datas are serialized with json.
"""


from time import sleep
import threading
import socket
import json
import asyncio
try:
    import signal
except ImportError:
    signal = None
from buggygame import Game
from get_my_ip3 import get_my_ip


MULTICAST_ADDR = "224.0.0.11", 18888
PORT = 8888
HOST = get_my_ip()

class MyServerUdpProtocol:
    def __init__(self):
        # Instance Game
        self.mygame = Game(arduino, sensor)

        # Envoi de l'IP toutes les secondes
        thread1 = threading.Thread(target=self.send_ip_loop)
        thread1.start()

        # Socket multicast
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def connection_made(self, transport):
        print('Server starting ...')
        self.transport = transport

    def datagram_received(self, data, addr):
        '''Le serveur répond à chaque requête du client'''

        # Traitement des données reçues
        self.update(data, addr)
        # Récup de la réponse
        resp = self.mygame.svr_resp
        ##if resp:
            ##print("Envoi de {}".format(resp.decode("utf-8")))
        # Envoi de la réponse (ou pas)
        try:
            if self.mygame.resp:
                self.transport.sendto(resp, addr)
        except:
            print("A priori le réseau est HS, je ne peux pas envoyer")

    def update(self, data, addr):
        # Tri des messages et création de la réponse
        self.mygame.sorting_messages(data, addr)
        # Vérification des déconnectés, self.mygame.connected pas utilisé
        self.mygame.update_connected_player()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print('stop', exc)

    def send_mcast_ip(self):
        """Send over multicast.: {"Ip Adress": "192.168.1.4"}"""

        mcast = {'Ip Adress': HOST}

        resp = json.dumps(mcast).encode("utf-8")
        #print("Envoi de {}".format(resp))
        try:
            self.sock.sendto(resp, MULTICAST_ADDR)
        except:
            print("A priori le réseau est HS, je ne peux pas envoyer en multicast")

    def send_ip_loop(self):
        """Envoi toutes les secondes de l'adresse ip du serveur sur le Multicast"""
        while True:
            sleep(1)
            self.send_mcast_ip()
            # Update always
            self.mygame.update_connected_player()


def start_server(loop, addr):
    t = asyncio.Task(loop.create_datagram_endpoint(
        MyServerUdpProtocol, local_addr=addr))
    transport, server = loop.run_until_complete(t)
    return transport

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    if signal is not None:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    server = start_server(loop, (HOST, PORT))
    try:
        print("Le serveur UDP tourne IP =", HOST, "port =", PORT)
        loop.run_forever()
    finally:
        server.close()
        loop.close()
