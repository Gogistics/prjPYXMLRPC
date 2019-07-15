# -*- coding: utf-8 -*-
#
# Author:
#   Alan Tai
# Program:
#   Controller
# Date:
#   7/13/2019

import subprocess
import os
import socket
from pymongo import MongoClient
import sys

#c set env variables
HOSTNAME = socket.gethostname()    
IPAddr = socket.gethostbyname(HOSTNAME) 

if __name__ == "__main__":
    print("HOSTNAME: {HOSTNAME}".format(HOSTNAME=HOSTNAME))
    print("IPAddr: {IPAddr}".format(IPAddr=IPAddr))
    try:
        p1 = subprocess.Popen(["python3", "-u", "app_data_manager/app.py"],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
        print("Start up app_config_handler...")

        p2 = subprocess.Popen(["python3", "-u", "app_fan_controller/app.py"],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
        print("Start up app_fan_controller...")

        output1, err1 = p1.communicate()
        output2, err2 = p2.communicate()
    except subprocess.CalledProcessError as e:
        print("Unable to start up the control system!")
        print(e.output)
