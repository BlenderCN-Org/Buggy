#!/usr/bin/python3
# -*- coding: UTF-8 -*-

## send_config.py

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

from bge import logic as gl
import json
import subprocess, re
from functools import reduce
from client import Client

def get_all_obj_in_dict():
    ''' Get all blender objects from all scenes in a dict {object.name: object}.
        Very usefull but objDict is argument in all functions'''
    scenes = gl.getSceneList()
    objDict = {}
    for scn in scenes:
        for obj in scn.objects:
            objDict[obj.name] = obj
    return objDict

def get_my_ip():
    # Retourne l'adresse ip du pc sur le réseau local

    #A generator that returns stripped lines of output from "ip address show"
    iplines=(line.strip() for line in subprocess.getoutput("ip address show")\
                                                                .split('\n'))
    #Turn that into a list of IPv4 and IPv6 address/mask strings
    addresses1=reduce(lambda a,v:a+v,(re.findall(r"inet ([\d.]+/\d+)",line) +\
                                        re.findall(r"inet6 ([\:\da-f]+/\d+)",
                                        line) for line in iplines))
    #Get a list of IPv4 addresses as (IPstring,subnetsize) tuples
    ipv4s=[(ip,int(subnet)) for ip,subnet in (addr.split('/') for addr in \
                                                addresses1 if '.' in addr)]
    # my IP
    try:
        ip = ipv4s[1][0]
    except:
        print("Cet ordinateur n'est pas connecté à un réseau !")
        ip = "127.0.0.1"
    return ip

def main():
    objDict = get_all_obj_in_dict()
    controller = gl.getCurrentController()
    owner = controller.owner

    if not owner["connected"]:
        gl.ip = get_my_ip()
        gl.myclient = Client(gl.ip, 8888, 1024, False)
        owner["connected"] = True

    if owner["connected"]:
        reset = objDict["reset"]["reset"]
        if reset == False: # json don't understand true false
            reset = 0
        else:
            reset = 1
        start = objDict["start"]["start"]
        if start == False:
            start = 0
        else:
            start = 1
        level = objDict["l"]["Text"]

        d = {"From server GUI": {"reset": reset, "start": start, "level": level}}
        # Send
        jsondata = json.dumps(d).encode("utf-8")
        try:
            gl.myclient.send(jsondata)
        except:
            print("No connected")
            owner["Text"] = "No connected"
            owner["connected"] = False

main()
