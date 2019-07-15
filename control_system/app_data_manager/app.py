#!/bin/python3
# -*- coding: utf-8 -*-
#
# Author:
#   Alan Tai
# Program:
#   Application of configuring all subsystems and fan controllers
#   and save the data into Postgres at startup or during the operation.
#   This application also received subsystems' temperatures and save temporary data in Redis
# Date:
#   7/13/2019

# sys
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import os
import datetime
import socket
import time
import syslog
import sys
# \sys

# dbs
import psycopg2
from pymongo import MongoClient
import redis
# \dbs

# set env variables
# TODO: create a global variables handler to manage all global variables
HOSTNAME = socket.gethostname()
IPAddr = socket.gethostbyname(HOSTNAME)
CONTROLLER_ID = os.environ["CONTROLLER_ID"]
CONTROLLER_IP = os.environ["CONTROLLER_IP"]
CONTROLLER_PORT = int(os.environ["CONTROLLER_PORT"])

# dbs
MONGO_IP = os.environ["MONGO_IP"]
MONGO_PORT = int(os.environ["MONGO_PORT"])
MONGO_DB = os.environ["MONGO_DB"]
MONGO_COLLECTION_LOGS = os.environ["MONGO_COLLECTION_LOGS"]

REDIS_IP = os.environ["REDIS_IP"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_DB = int(os.environ["REDIS_DB"])

POSTGRES_IP = os.environ["POSTGRES_IP"]
POSTGRES_PORT = int(os.environ["POSTGRES_PORT"])
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
# \dbs
# \set env variables

# DBs setup
# Mongo setup
try:
    client = MongoClient(MONGO_IP, MONGO_PORT)
    db = client[MONGO_DB]
    logs = db[MONGO_COLLECTION_LOGS]
    # log succeeded to connect to Postgres
    tstz = str(datetime.datetime.utcnow())
    event_str = """
        Data manager established the connection to Mongo:
        host => {MONGO_IP} ;
        port => {MONGO_PORT} ;
        db => {MONGO_DB} ;
        collection => {MONGO_COLLECTION_LOGS}
    """.format(MONGO_IP = MONGO_IP,
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
        Unable to connect to Mongo so logging the error by syslog for the triage.
        Error: {ERR}
    """.format(ERR = e).rstrip()
    syslog.syslog(syslog.LOG_ERR, event_str)
    sys.exit(0)
# \Mongo setup
# \DBs setup

# Redis setup
try:
    rd = redis.Redis(host = REDIS_IP,
                    port = REDIS_PORT,
                    db = REDIS_DB)

    # log succeeded to connect to Redis
    tstz = str(datetime.datetime.utcnow())
    event_str = """
        Data manager established the connection to Redis;
        host => {REDIS_IP} ;
        port => {REDIS_PORT} ;
        db => {REDIS_DB}
    """.format(REDIS_IP = REDIS_IP,
            REDIS_PORT = REDIS_PORT,
            REDIS_DB = REDIS_DB).rstrip()
    log = {
        "log_level": syslog.LOG_INFO,
        "event": event_str,
        "timestamp_utc": tstz
    }
    log_id = logs.insert_one(log).inserted_id
except BaseException as e:
    # log failed to connect to Redis
    tstz = str(datetime.datetime.utcnow())
    event_str = """
        Data manager failed to connected to Redis.
        host => {REDIS_IP} ;
        port => {REDIS_PORT} ;
        db => {REDIS_DB}
        Error: {ERR}
    """.format(REDIS_IP = REDIS_IP,
            REDIS_PORT = REDIS_PORT,
            REDIS_DB = REDIS_DB,
            ERR = e).rstrip()
    log = {
        "log_level": syslog.LOG_ERR,
        "event": event_str,
        "timestamp_utc": tstz
    }
    log_id = logs.insert_one(log).inserted_id
    sys.exit(0)
# \Redis setup

# Postgres setup
try:
    conn_str = """
        dbname={POSTGRES_DB}
        user={POSTGRES_USER}
        host={POSTGRES_IP}
    """.format(POSTGRES_DB = POSTGRES_DB,
            POSTGRES_USER = POSTGRES_USER,
            POSTGRES_IP = POSTGRES_IP).replace('"', "'")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    # log succeeded to connect to Postgres
    tstz = str(datetime.datetime.utcnow())
    event_str = """
        Data manager established the connection to Postgres:
        host => {POSTGRES_IP} ;
        user => {POSTGRES_USER} ;
        dbname => {POSTGRES_DB}
    """.format(POSTGRES_DB = POSTGRES_DB,
            POSTGRES_USER = POSTGRES_USER,
            POSTGRES_IP = POSTGRES_IP).rstrip()
    log = {
        "log_level": syslog.LOG_INFO,
        "event": event_str,
        "timestamp_utc": tstz
    }
    log_id = logs.insert_one(log).inserted_id
except BaseException as e:
    # log failed to connect to Postgres
    tstz = str(datetime.datetime.utcnow())
    event_str = """
        Data manager failed to connected to Postgres:
        host => {POSTGRES_IP} ;
        user => {POSTGRES_USER} ;
        dbname => {POSTGRES_DB}
        Error: {ERR}
    """.format(POSTGRES_DB = POSTGRES_DB,
            POSTGRES_USER = POSTGRES_USER,
            POSTGRES_IP = POSTGRES_IP,
            ERR = e).rstrip()
    log = {
        "log_level": syslog.LOG_ERR,
        "event": event_str,
        "timestamp_utc": tstz
    }
    log_id = logs.insert_one(log).inserted_id
    sys.exit(0)
# \Postgres setup


def start_data_manager():
    # XMLRPC Handler
    class AppDataManager(SimpleXMLRPCRequestHandler):
        rpc_paths = ("/RPC2",)

    # Note: Suggest moving the functions of handling registration to app_config_handler/app.py
    #       and rename app_data_manager to app_state_data_handler.
    #       This way, each container can perform its own fucntions and debugging can be facilitated
    with SimpleXMLRPCServer((CONTROLLER_IP, CONTROLLER_PORT),
                            requestHandler = AppDataManager) as server:
        server.register_introspection_functions()

        # Register a function under function.__name__.
        @server.register_function
        def register_subsystem(params):
            """ a mechanism for subsystem registration """

            # store subsystem info. into Postgres if not exist
            tstz = str(datetime.datetime.utcnow())
            psql_str = """
                INSERT INTO configuration_subsystem (comp_id, ip, port, tstz)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """
            values = (params["SUBSYS_ID"], params["IPAddr"], params["PORT"], tstz)
            cur.execute(psql_str, values)
            conn.commit()

            # log registration
            event_str = """
                A new subsystem, {SUBSYS_ID}, registered and its info. got stored in Postgres
            """.format(SUBSYS_ID=params["SUBSYS_ID"]).rstrip()
            log = {
                "log_level": syslog.LOG_INFO,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id

            # STATUS_CODE:
            # 0: failed
            # 1: succeeded
            resp = {"STATUS_CODE": 1,
                    "CONTROLLER_ID": CONTROLLER_ID}
            return resp

        @server.register_function
        def register_fan(params):
            """ a mechanism for fan system registration """
            tstz = str(datetime.datetime.utcnow())
            FAN_ID = params["FAN_ID"]
            FAN_IP = params["IPAddr"]
            FAN_PORT = params["PORT"]

            # store fan system info. into Postgres if not exist
            psql_str = """
                INSERT INTO configuration_fan (comp_id, ip, port, tstz)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """
            values = (FAN_ID, FAN_IP, FAN_PORT, tstz)
            cur.execute(psql_str, values)
            conn.commit()

            # STATUS_CODE:
            # 0: failed
            # 1: succeeded
            resp = {"STATUS_CODE": 1,
                    "CONTROLLER_ID": CONTROLLER_ID}
            return resp

        @server.register_function
        def report_temperature(params):
            SUBSYS_ID = params["SUBSYS_ID"]
            TEMPERATURE = int(params["TEMPERATURE"])
            tstz = str(datetime.datetime.utcnow())

            # update sussystem temperature
            rd.hset(SUBSYS_ID, "TEMPERATURE", TEMPERATURE)

            # find max temperature
            SUBSYS_MAX_TEMPERATURE = None
            subsystem_ids = rd.keys("SUBSYS-*")
            for subsystem_id in subsystem_ids:
                # find max temperature
                tmp_temperature = int(rd.hget(subsystem_id, "TEMPERATURE"))
                if (SUBSYS_MAX_TEMPERATURE is None) or (SUBSYS_MAX_TEMPERATURE < tmp_temperature):
                    SUBSYS_MAX_TEMPERATURE = tmp_temperature
            rd.hset("SUBSYS", "MAX_TEMPERATURE", SUBSYS_MAX_TEMPERATURE)

            # log the event of reporting temperature
            event_str = """
                Subsystem, {SUBSYS_ID}, reports its temperature {TEMPERATURE}
            """.format(SUBSYS_ID = SUBSYS_ID,
                    TEMPERATURE = TEMPERATURE).rstrip()
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
        # \Register a function under function.__name__.

        # start the server
        try:
            server.serve_forever()
        except BaseException as e:
            # log failed case
            event_str = """
                Control system, {CONTROLLER_ID}, failed to start up data manager.
                Error: {ERR}
            """.format(CONTROLLER_ID = CONTROLLER_ID,
                    ERR = e).rstrip()
            log = {
                "log_level": syslog.LOG_ERR,
                "event": event_str,
                "timestamp_utc": tstz
            }
            log_id = logs.insert_one(log).inserted_id
            sys.exit(0)

if __name__ == "__main__":
    start_data_manager()
