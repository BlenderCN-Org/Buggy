#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## client.py

#############################################################################
# Copyright (C) Labomedia June 2015
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


class Client:
    '''Send and Receive with the same socket.

    Send a request, and get the response of a sever.
    datas aren't encoded and decoded in this class.
    Use datagram_decode.py to decode.
    '''

    def __init__(self, ip, port, buffer_size=1024, verbose=False):
        '''Plug an UDP socket.
        ip example: "localhost", "127.0.0.1", "10.0.0.100"
        port = integer
        buffer_size = integer, used to clear out the buffer at each reading
        verbose = True is very verbose in terminal
        '''
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.verb = verbose
        self.conn = False
        self.data = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            #self.sock.bind((self.ip, self.port))
            self.sock.setblocking(False)
            self.sock.settimeout(0.01)
            # This option set buffer size
            # Every self.sock.recv() empty the buffer,
            # so we have always the last incomming value
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                 buffer_size)
            if self.verb:
                print('Plug : IP = {} Port = {} Buffer Size = {}'.
                      format(ip, port, buffer_size))
        except:
            if self.verb:
                print('No connected on {0}:{1}'.format(self.ip, self.port))

    def send(self, req):
        '''Send request to connected socket.'''
        addr = self.ip, self.port
        self.sock.connect(addr)
        self.sock.send(req)
        if self.verb:
            print('{0} sended'.format(req))

    def send_to(self, req, address):
        '''Send request to address = (ip, port)
        '''
        self.sock.sendto(req, address)
        if self.verb:
            print('{0} sended'.format(req))

    def listen(self):
        '''Return received data and address from.'''
        raw_data, addr = None, None
        try:
            raw_data, addr = self.sock.recvfrom(self.buffer_size)
            if self.verb:
                print("Binary received from {0}: {1}".format(addr, raw_data))
        except:
            if self.verb:
                print('Received nothing')
        return raw_data, addr
