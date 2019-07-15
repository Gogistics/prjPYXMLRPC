# -*- coding: utf-8 -*-
#
# Author:
#   Alan Tai
# Program:
#   Application of adjusting the fan speed
# Date:
#   7/13/2019

# sys
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import datetime
import time
import xmlrpc.client
import socket
import os
import syslog
import sys
# \sys

# dbs
from pymongo import MongoClient
# \dbs

# set env variables
# TODO: create a global variables handler to manage all global variables
FAN_ID = os.environ["FAN_ID"]
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
        Fan, {FAN_ID}, established the connection to Mongo:
        host => {MONGO_IP} ;
        port => {MONGO_PORT} ;
        db => {MONGO_DB} ;
        collection => {MONGO_COLLECTION_LOGS}
    """.format(FAN_ID = FAN_ID,
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
        Unable to connect to Mongo so logging the error by syslog for the triage
    """.format(ERR = e).rstrip()
    syslog.syslog(syslog.LOG_ERR, event_str)
    sys.exit(0)
# \Mongo setup


def start_up_fan():
    # register to the control system
    while True:
        # try until succeed
        ctrl_config_proxy_conn = "http://{CONTROLLER_IP}:{CONTROLLER_PORT}".format(CONTROLLER_IP = CONTROLLER_IP,
                                                                                CONTROLLER_PORT = CONTROLLER_PORT)
        ctrl_config_proxy = xmlrpc.client.ServerProxy(ctrl_config_proxy_conn)

        # register the fan to control system
        params = {
            "FAN_ID": FAN_ID,
            "IPAddr": IPAddr,
            "PORT": EXPOSE_PORT
        }
        resp = ctrl_config_proxy.register_fan(params)
        print(resp)
        if resp["STATUS_CODE"] == 1:
            # log registration
            event_str = """
                Fan, {FAN_ID}, successfully registered in the control system and its info. got stored in Postgres
            """.format(FAN_ID = FAN_ID).rstrip()
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
                Fan, {FAN_ID}, failed to register in the control system
            """.format(FAN_ID = FAN_ID).rstrip()
            log = {
                "log_level": syslog.LOG_ERR,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id
            time.sleep(3)

    # \register to the control system

    class FanSystemHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ("/RPC2",)

    with SimpleXMLRPCServer((IPAddr, EXPOSE_PORT),
                            requestHandler = FanSystemHandler) as server:
        server.register_introspection_functions()

        @server.register_function
        def send_control_signal(params):
            print("params from control system: {params}".format(params = params))

            # TODO (not required in this coding task): pass PERCENTAGE_OF_MAX_SPEED to the real controller to adjust the fan speed
            PERCENTAGE_OF_MAX_SPEED = params["PERCENTAGE_OF_MAX_SPEED"]
            # log registration
            event_str = """
                Fan, {FAN_ID}, got PERCENTAGE_OF_MAX_SPEED, {PERCENTAGE_OF_MAX_SPEED}, from control system
            """.format(FAN_ID = FAN_ID,
                    PERCENTAGE_OF_MAX_SPEED = PERCENTAGE_OF_MAX_SPEED).rstrip()
            log = {
                "log_level": syslog.LOG_INFO,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id

            # STATUS_CODE:
            # 0: failed
            # 1: succeeded
            resp = {"STATUS_CODE": 1}
            return resp

        try:
            server.serve_forever()
        except BaseException as e:
            print("Unable to spin up rpx server")
            print("Unknown error {err}".format(err = e))
            sys.exit(0)

if __name__ == "__main__":
    print("Fan Info. ===> ")
    print("HOSTNAME: {HOSTNAME}".format(HOSTNAME = HOSTNAME))
    print("IPAddr: {IPAddr}".format(IPAddr = IPAddr))
    print("FAN_ID: {FAN_ID}".format(FAN_ID = FAN_ID))
    start_up_fan()
