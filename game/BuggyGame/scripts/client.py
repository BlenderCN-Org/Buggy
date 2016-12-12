#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## client.py

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


import socket


class Client:
    '''Envoi et reception en UDP.'''

    def __init__(self, ip, port, buffer_size=1024, timeout=0.01):
        '''Plug an UDP socket.
        ip = "localhost" ou "127.0.0.1" ou "10.0.0.100"
        port = integer
        buffer_size = entier, permet de vider le buffer à chaque lecture,
        pour avoir toujours la
        '''

        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.conn = False
        self.data = None

        # Socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.setblocking(False)
            self.sock.settimeout(self.timeout)
            # This option set buffer size
            # Every self.sock.recv() empty the buffer,
            # so we have always the last incomming value
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                 buffer_size)
        except:
            print("Erreur à la création du socket UDP {}:{}".format(self.ip,
                                                                self.port))

    def send(self, req):
        """Send request to connected socket."""

        addr = self.ip, self.port
        self.sock.send(req)

    def send_to(self, req, address):
        """Send request to address = (ip, port)."""

        self.sock.sendto(req, address)

    def listen(self):
        '''Return received data and address from.'''

        raw_data, addr = None, None
        try:
            raw_data, addr = self.sock.recvfrom(self.buffer_size)
        except:
            print("Erreur à la réception du socket UDP {}:{}".format(self.ip,
                                                                self.port))
        return raw_data, addr
