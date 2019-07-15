# -*- coding: utf-8 -*-
#
# Author:
#   Alan Tai
# Program:
#   Application of reporting temperature and logs to control application (WIP)
# Date:
#   7/13/2019

# sys
import xmlrpc.client
import datetime
import time
import socket
import os
import random
import syslog
import sys
# \sys

# dbs
from pymongo import MongoClient
# \dbs


# set env variables
# TODO: create a global variables handler to manage all global variables
SUBSYS_ID = os.environ["SUBSYS_ID"]
EXPOSE_PORT = int(os.environ["EXPOSE_PORT"])
HOSTNAME = socket.gethostname()
IPAddr = socket.gethostbyname(HOSTNAME)

CONTROLLER_IP = os.environ["CONTROLLER_IP"]
CONTROLLER_PORT = os.environ["CONTROLLER_PORT"]

MONGO_IP = os.environ["MONGO_IP"]
MONGO_PORT = int(os.environ["MONGO_PORT"])
MONGO_DB = os.environ["MONGO_DB"]
MONGO_COLLECTION_LOGS = os.environ["MONGO_COLLECTION_LOGS"]
# \set env variables


# Mongo setup
try:
    client = MongoClient(MONGO_IP, MONGO_PORT)
    db = client[MONGO_DB]
    logs = db[MONGO_COLLECTION_LOGS]
    # log succeeded to connect to Postgres
    tstz = str(datetime.datetime.utcnow())
    event_str = """
        Subsystem, {SUBSYS_ID},Connected to Mongo:
        host => {MONGO_IP} ;
        port => {MONGO_PORT} ;
        db => {MONGO_DB} ;
        collection => {MONGO_COLLECTION_LOGS}
    """.format(SUBSYS_ID = SUBSYS_ID,
            MONGO_IP = MONGO_IP,
            MONGO_PORT = MONGO_PORT,
            MONGO_DB = MONGO_DB,
            MONGO_COLLECTION_LOGS = MONGO_COLLECTION_LOGS).rstrip()
    log = {
        "log_level": syslog.LOG_INFO,
        "event": event_str,
        "timestamp_utc": tstz
    }
    log_id = logs.insert_one(log).inserted_id
except BaseException as e:
    event_str = """
        Unable to connect to Mongo so logging the error by syslog for the triage. Error: {ERR}
    """.format(ERR = e).rstrip()
    syslog.syslog(syslog.LOG_ERR, event_str)
    sys.exit(0)
# \Mongo setup


# def section
def start_up_subsystem():
    # register to the control system
    while True:
        ctrl_config_proxy_conn = "http://{CONTROLLER_IP}:{CONTROLLER_PORT}".format(CONTROLLER_IP = CONTROLLER_IP,
                                                                                CONTROLLER_PORT = CONTROLLER_PORT)
        ctrl_config_proxy = xmlrpc.client.ServerProxy(ctrl_config_proxy_conn)

        # register the subsystem to control system
        params = {
            "SUBSYS_ID": SUBSYS_ID,
            "IPAddr": IPAddr,
            "PORT": EXPOSE_PORT
        }
        resp = ctrl_config_proxy.register_subsystem(params)
        print(resp)
        if resp["STATUS_CODE"] == 1:
            # log registration
            event_str = """
                Subsystem, {SUBSYS_ID}, successfully registered in the control system and its info. got stored in Postgres
            """.format(SUBSYS_ID = SUBSYS_ID).rstrip()
            log = {
                "log_level": syslog.LOG_INFO,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id
            break;
        else:
            print("try to connect to control system after 3 sec...")
            # log failed case
            event_str = """
                Subsystem, {SUBSYS_ID}, failed to register in the control system
            """.format(SUBSYS_ID = SUBSYS_ID).rstrip()
            log = {
                "log_level": syslog.LOG_ERR,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id
            time.sleep(3)

    # periodically report its temperature to the control system
    while True:
        fake_temperature = random.randint(0,100)
        params = {
            "SUBSYS_ID": SUBSYS_ID,
            "TEMPERATURE": fake_temperature
        }
        resp = ctrl_config_proxy.report_temperature(params)
        print(resp)
        if resp["STATUS_CODE"] == 1:
            # log report status
            event_str = """
                Subsystem, {SUBSYS_ID}, successfully report its temperature to the control system
            """.format(SUBSYS_ID = SUBSYS_ID).rstrip()
            log = {
                "log_level": syslog.LOG_INFO,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id
        else:
            # log failed case
            event_str = """
                Subsystem, {SUBSYS_ID}, failed to report its temperature to the control system
            """.format(SUBSYS_ID = SUBSYS_ID).rstrip()
            log = {
                "log_level": syslog.LOG_ERR,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id

        # wait for 3 sec to send new temperature to controller
        time.sleep(3)

if __name__ == "__main__":
    print("Subsystem Info. ===> ")
    print("HOSTNAME: {HOSTNAME}".format(HOSTNAME = HOSTNAME))
    print("IPAddr: {IPAddr}".format(IPAddr = IPAddr))
    print("SUBSYS_ID: {SUBSYS_ID}".format(SUBSYS_ID = SUBSYS_ID))
    start_up_subsystem()
