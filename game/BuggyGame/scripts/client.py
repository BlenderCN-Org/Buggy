#!/usr/bin/python3
# -*- coding: UTF-8 -*-



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
