#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## multicastreceiver.py

#############################################################################
# Copyright (C) Labomedia July 2014
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


import socket


class MulticastReceiver():
    ''' Récupère les datas OSC en Multicast, décode'''
    def __init__(self, ip, port, buffer_size=1024, bavard=True):
        self.ANY = "0.0.0.0"
        self.MCAST_ADDR = ip
        self.MCAST_PORT = port
        self.sock = None
        self.buffer_size = buffer_size
        self.bavard = bavard

    def connexion(self):
        '''Création d'un socket multicast self.sock.'''
        # Création d'un socket
        try:
            #create a UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                        socket.IPPROTO_UDP)
            #allow multiple sockets to use the same PORT number
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            #Bind to the port that we know will receive multicast data
            self.sock.bind((self.ANY, self.MCAST_PORT))
            #tell the kernel that we are a multicast socket
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                                    255)
            #Tell the kernel that we want to add ourselves to a multicast group
            #The address for the multicast group is the third param
            status = self.sock.setsockopt(socket.IPPROTO_IP,
                                            socket.IP_ADD_MEMBERSHIP,
                                            socket.inet_aton(self.MCAST_ADDR)\
                                            + socket.inet_aton(self.ANY))
            self.sock.setblocking(0)
            # Limite la taille du buffer UDP pour éviter la latence,
            # le buffer est vidé à chaque lecture
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                    self.buffer_size)
            if self.bavard:
                print("Réception des datas OSC sur :")
                print("IP = {} : Port = {}  avec un Buffer = {}\n".format(\
                        self.MCAST_ADDR, self.MCAST_PORT, self.buffer_size))
        except:
            print("Pas de connexion sur IP={} Port={}".format(self.MCAST_ADDR,
                                                            self.MCAST_PORT))

    def receive(self):
        '''Return raw data received on multicast.'''
        raw_data = None
        try:
            raw_data = self.sock.recv(self.buffer_size)
            if self.bavard:
                print("Multicast data received = {0}".format(raw_data))
        except socket.error:
            if self.bavard:
                print("Pas de reception dans la fonction receive() de MulticastReceiver")
        return raw_data
