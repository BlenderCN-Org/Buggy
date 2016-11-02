#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## network.py

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
from client import Client
import json
import ast
from multicastreceiver import MulticastReceiver


def main():
    if not gl.network:
        gl.network = True
        gl.myclient = Client(gl.ipServer, gl.portOut, 1024, False)
        gl.mymulticast = MulticastReceiver(gl.multicastip, gl.multicastport,
                                            1024, False)
        gl.mymulticast.connexion()

    if gl.network:
        update_receive()
        # Récupération de l'IP du serveur sur le Multicast toutes les 1 seconde
        if gl.tempoDict["always"].tempo % 60 == 0:
            update_multicast_receive()
        #if gl.state == "Race":
        send_to_server()

def update_multicast_receive():
    """mcast = {"Multicast": {'Ip Adress': "127.0.0.1",
                              'Dictateur': {'dbv_exist': 0, 'dbv_name': 'toto'}}}
    """
    raw_data = gl.mymulticast.receive()
    # Get ip in raw_data
    if raw_data:
        msg = ast.literal_eval(raw_data.decode("utf-8"))
        # print(msg) {"Ip Adress": "192.168.1.5"}
        if 'Ip Adress' in msg:
            gl.ipServer = msg['Ip Adress']
            gl.server = True

def send_to_server():
    mydata = {}
    try:
        mydata["time"] = gl.time[gl.level - 1][gl.myPosition]
    except:
        mydata["time"] = 0
    try:
        mydata["name"] = gl.my_name
    except:
        mydata["name"] = "nobody"
    try:
        loc, rot = gl.carDict[gl.myPosition].Loc_Rot
        # Matrix and vectors aren't json serializable
        mydata["loc"] = [   int(100 * loc[0]),
                            int(100 * loc[1]),
                            int(100 * loc[2]) ]
        mydata["rot"] = [
                        [   int(100 * rot[0][0]),
                            int(100 * rot[0][1]),
                            int(100 * rot[0][2]) ],
                        [   int(100 * rot[1][0]),
                            int(100 * rot[1][1]),
                            int(100 * rot[1][2]) ],
                        [   int(100 * rot[2][0]),
                            int(100 * rot[2][1]),
                            int(100 * rot[2][2]) ]
                        ]
    except:
        loc, rot = [0, 0, -5] , [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    # Crée une entête pour le serveur
    alldata = {"joueur": mydata}
    #print("data sended by blender", alldata)
    jsondata = json.dumps(alldata).encode("utf-8")

    # Send
    address = (gl.ipServer, gl.portOut)
    gl.myclient.send_to(jsondata, address)

def update_receive():
    raw_data, addr = gl.myclient.listen()
    # Decode json data
    if raw_data is not None:
        gl.server = True
        data = json.loads(raw_data.decode("utf-8"))
        recup_messages(data)

def update_position():
    # Recalcul de ma position
    gl.myPosition = 0
    if gl.myIp in gl.cars:
        #print(gl.cars)
        gl.myPosition = gl.cars[gl.myIp]["position"]

def recup_messages(data):
    """From data = ...
    """

    if "players" in data:
        # Recup de players
        gl.cars = data["players"]

        # Le serveur donne les positions, réactualisé en permanence
        # actualise gl.myPosition
        if len(data["players"]) > 0:
            update_position()

    if "buggygame" in data:
        # Recup de buggygame qui vient du server GUI
        buggygame = data["buggygame"]
        gl.level = buggygame["level"]
        gl.classement = buggygame["classement"]
        gl.start = buggygame["start"]
        gl.reset = buggygame["reset"]

    if "Game" in data:
        # Recup de buggygame
        game = data["Game"]
        gl.level = game["level"]
        gl.start = game["start"]
        gl.reset = game["reset"]

    if "phone" in data:
        # Recup de phone
        # data["phone"][gl.myIp]={'acc': 4, 'brake': 0, 'accel': 0}
        # who are you fera la correspondance gl.my_name avec ip téléphone
        if gl.my_name in data["phone"]:
            gl.wheel = 1  # je reçois les datas de mon Wheel
            my_phone = data["phone"][gl.my_name]
            # gl.phone = [accy, accel, brake]
            gl.phone[0] = my_phone["accy"]
            gl.phone[1] = my_phone["accel"]
            gl.phone[2] = my_phone["brake"]
            if "tuning" in my_phone:
                gl.tuning = my_phone["tuning"]

        else:
            # TODO: à vérifier
            gl.wheel = 0

    if "rotation" in data:
        # Récup rotation du casque
        gl.rot = data["rotation"]  # liste de 3: x, y, z
