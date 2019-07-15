# -*- coding: utf-8 -*-
#
# Author:
#   Alan Tai
# Program:
#   Application of calculating the percentage of max fan speed with the data stored in Redis and Postgres,
#   and sending the signals to all fans
# Date:
#   7/20/2019

# sys
import xmlrpc.client
import os
import socket
import datetime
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
        Fan controller established the connection to Mongo:
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
        Fan controller established the connection to Redis;
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
        Fan controller failed to connected to Redis.
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
        Fan controller established the connection to Postgres:
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
        Fan controller failed to connected to Postgres:
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

def start_fan_controller():
    # Send control signal to each fan
    while  True:
        # get max temperature from Redis

        # check if SUBSYS_MAX_TEMPERATURE is type integer
        SUBSYS_MAX_TEMPERATURE = rd.hget('SUBSYS', 'MAX_TEMPERATURE')
        if SUBSYS_MAX_TEMPERATURE is not None:
            SUBSYS_MAX_TEMPERATURE = int(SUBSYS_MAX_TEMPERATURE)
        else:
            # wait for 5 sec to check SUBSYS_MAX_TEMPERATURE type again
            time.sleep(5)
            continue

        # calcuate the percentage of max fan speed of each fan
        # Note: According to the requirements, The maximum speed may be different for different fans
        #       so here the calculation is for the percentage of max fan speed
        #       and the percentage will be sent each fan
        PERCENTAGE_OF_MAX_SPEED = 0 # default value percentage of max fan speed

        # Requiremenets:
        # * All fans should be set to the same percentage of max speed.
        # * If the temperature is 25°C or below, the fans should run at 20% of max speed.
        # * If the temperature is 75°C or above, the fans should run at 100% of max speed.
        # * If the maximum measured subsystem temperature is in between 25°C and 75°C,
        #   the fans should run at a percentage of max speed linearly interpolated between 20% and 100%.
        if SUBSYS_MAX_TEMPERATURE <= 25:
            PERCENTAGE_OF_MAX_SPEED = 20
        elif SUBSYS_MAX_TEMPERATURE >= 75:
            PERCENTAGE_OF_MAX_SPEED = 100
        elif SUBSYS_MAX_TEMPERATURE > 25 and SUBSYS_MAX_TEMPERATURE < 75:
            PERCENTAGE_OF_MAX_SPEED = 20 + round((SUBSYS_MAX_TEMPERATURE - 25) * ((100 - 20) / (75 - 25)), 2)

        # query fans' ids
        cur.execute('SELECT comp_id, ip, port FROM configuration_fan;')
        fans = cur.fetchall()

        # loop through fans to send control signal to each fan
        for fan in fans:
            # calculate control signal based on the max temperature
            FAN_ID = fan[0]
            FAN_IP = fan[1]
            FAN_PORT = fan[2]
            try:
                # send control signal to fan controller

                # set fan proxy
                fan_proxy_conn = "http://{FAN_IP}:{FAN_PORT}".format(FAN_IP = FAN_IP,
                                                                    FAN_PORT = FAN_PORT)
                fan_proxy = xmlrpc.client.ServerProxy(fan_proxy_conn)
                params = {
                    'FAN_ID': FAN_ID,
                    'SUBSYS_MAX_TEMPERATURE': SUBSYS_MAX_TEMPERATURE,
                    'PERCENTAGE_OF_MAX_SPEED': PERCENTAGE_OF_MAX_SPEED
                }
                resp = fan_proxy.send_control_signal(params)
                print(resp)
                tstz = str(datetime.datetime.utcnow())
                log = None
                event_str = None
                if resp['STATUS_CODE'] != 1:
                    # log successful case
                    event_str = """
                        Controller failed to send control signal to the {FAN_ID} with adjusted speend {PERCENTAGE_OF_MAX_SPEED}
                    """.format(FAN_ID=FAN_ID,
                            PERCENTAGE_OF_MAX_SPEED=PERCENTAGE_OF_MAX_SPEED).rstrip()
                    log = {
                        'log_level': syslog.LOG_ERR,
                        'event': event_str,
                        'timestamp_utc': tstz
                    }
                else:
                    # log failed case
                    event_str = """
                        Controller sent control signal to the {FAN_ID} with adjusted speend {PERCENTAGE_OF_MAX_SPEED}
                    """.format(FAN_ID=FAN_ID,
                            PERCENTAGE_OF_MAX_SPEED=PERCENTAGE_OF_MAX_SPEED).rstrip()
                    log = {
                        'log_level': syslog.LOG_INFO,
                        'event': event_str,
                        'timestamp_utc': tstz
                    }
                log_id = logs.insert_one(log).inserted_id

                # wait for .3 sec
                time.sleep(.3)

            except BaseException as e:
                # log the failed event of sending control signal to the fan
                tstz = str(datetime.datetime.utcnow())
                event_str = """
                    Controller failed to send control signal to the {FAN_ID}.
                    Error: {ERR}
                """.format(FAN_ID=FAN_ID, ERR = e).rstrip()
                log = {
                    'log_level': syslog.LOG_ERR,
                    'event': event_str,
                    'timestamp_utc': tstz
                }
                log_id = logs.insert_one(log).inserted_id

        # send control signal to each fan every 2 sec
        time.sleep(2)
        # \# Send control signal to each fan

if __name__ == "__main__":
    start_fan_controller()
