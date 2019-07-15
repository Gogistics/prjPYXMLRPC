# Design of Robotics System

## Goal
The goal is to solve the problem described:
You are given a robot with many subsystems that each generate their own individual temperature measurement. There are also multiple fans onboard the robot that are used to cool the electronics to prevent overheating. Because the fans are very loud when running all the time, and because the robot operates alongside humans, the fan speeds are set so that the noise level is minimized without endangering the electronics. Conceptually the robot can be considered to be a set of IoT devices on a common network.

---

## Specification/Requirements

#### Spec. of the application
* The temperature of each subsystem is provided as a floating point number in °C via external communication to the subsystem.
* The number of subsystems and the number of fans present should both be configurable at startup, but you may assume that each of these numbers has an upper bound. You may assume that the number of each is constant after startup.
* The speed in RPM of each fan is managed by your system. You can assume that the plumbing to the low level hardware is managed for you after updating some internal state variable.
* The maximum speed may be different for different fans. You may assume that 0 RPM always represents 0% of max speed.
* Your system logs all the system data to an external location outside the subsystems.

#### Spec. of the fan control algorithm
* The most recent temperature measurements from each subsystem should be collected, and the fan max speed should be computed from the maximum of the most recent temperatures of all subsystems.
* All fans should be set to the same percentage of max speed.
* If the temperature is 25°C or below, the fans should run at 20% of max speed.
* If the temperature is 75°C or above, the fans should run at 100% of max speed.
* If the maximum measured subsystem temperature is in between 25°C and 75°C, the fans should run at a percentage of max speed linearly interpolated between 20% and 100%.

---

## Design concept
The design aims to solve the coding task of the robotics system by the microservices architecture. Microservices are a kind of service-oriented archtectures that construct a system as a colleciton of loosely coupled services. To simplify the communication between different applications, unidirectional data flow is recommended and implemented.

## Architecture diagram
This section is about the [architecture of the robot's systems](https://drive.google.com/file/d/17PLyc8d8U6ONpMeFGOvlmbNnkhTWT-kN/view?usp=sharing). Basically, the diagram comprises of four parts including databases, control system, subsystems, and fan systems, and also describes the relationships between all the mechanisms/componenets and the network design.


#### Databases
In terms of the databases, each type of databases only has an instance instead of master-slave cluster; for production services, it is recommended to have a setup of master-slave cluster because master node is for handling **write** operation and all slave nodes are for **read** operation.

* Redis
  In-memory database is used to store the temporary state data of all the subsystems

* Postgres
  SQL database is for storing the configuration data of all the subsystems and the fan systems

* Mongo
  NoSQL databases is for storing log data; in this coding task, the logs are piped to MongoDB by the Python applications. Further more, [syslog-ng can be installed and configured to pipe the logs to MongoDB](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.16/administration-guide/37).


#### Control system
In modern control theory, observability and controllability are crucial factors of a system; roughly speaking, a control system needs inputs from the measurement mechanism and then generates outputs to move a system to the desired states. In this coding task, the control system is designed to configure all the subsystems and the fan controllers by app_data_manager, collect the temperatures of all the subsystems by app_data_manager, and send control signals to the fan systems by app_fan_controller.

* Application of managing configuration and collecting temperature data from subsystem
  The control application can be simulated by XMLRPC server.

* Application of sending control signals to all fan systems
  The control application can be simulated by XMLRPC client.


#### Subsystems
* Application of registering itself to the control system and reporting the temperature of the subsystem itself and send logs to MongoDB.

#### Fan systems
* Application of receiving the percentage of max fan speend from the control system.

#### Network design
In this coding task, there is only one network, **172.99.0.0/16**.

---

## Code implementation

#### Explanation of the project directory

* control_system
This directory contains all stuff for bringing up the control system.
`control_system/main_controller.py` opens two subprocesses respectively running `app_data_manager/app.py` and `app_fan_controller/app.py`

* subsystems
This directory contains all stuff for bringing up all subsystems.
`subsystems/subsystem/app.py` runs the application of registering itself to the control system and sending its temperature to the control system.

* fans
This directory contains all stuff for bringing up all fan systems.
`fans/fan/app.py` runs the applications of registering itself to the control system and receiving the max percentage of fan speed from the control system.

* infra
This directory contains all stuff for the automation of the whole system (robotics system) setup. All applications and databases are running inside Docker containers that are based on Alpine OS.

---

## Testing

#### Prerequisites
1. Docker: Docker is used to simulate the whole system by running applications in different containers.
2. Bash 4+: Bash 4+ is needed for writing associate array; see `./infra/scripts/spin_up_subsystems.sh` and `./infra/scripts/spin_up_fans.sh` as references.

#### How to run tests
Once Docker gets installed and running properly, and Bash gets upgraded to 4+, execute `./infra/scripts/spin_up_whole_topology.sh` in the project directory.

#### Check results
View real time logging
```sh
$ docker logs -f <container-name/hash> # e.g. docker logs -f isi_fan_1
```

Check logs in MongoDB
```sh
$ docker exec -it isi_robot_system_mongo sh
/ # mongo
MongoDB shell version v4.0.6
connecting to: mongodb://127.0.0.1:27017/?gssapiServiceName=mongodb
Implicit session: session { "id" : UUID("b746395c-269d-4397-ba33-c918808f8e49") }
MongoDB server version: 4.0.6
Welcome to the MongoDB shell.
For interactive help, type "help".
For more comprehensive documentation, see
    http://docs.mongodb.org/
Questions? Try the support group
    http://groups.google.com/group/mongodb-user
Server has startup warnings: 
2019-07-24T22:44:42.604+0000 I STORAGE  [initandlisten] 
2019-07-24T22:44:42.604+0000 I STORAGE  [initandlisten] ** WARNING: Using the XFS filesystem is strongly recommended with the WiredTiger storage engine
2019-07-24T22:44:42.604+0000 I STORAGE  [initandlisten] **          See http://dochub.mongodb.org/core/prodnotes-filesystem
2019-07-24T22:44:43.041+0000 I CONTROL  [initandlisten] 
2019-07-24T22:44:43.041+0000 I CONTROL  [initandlisten] ** WARNING: Access control is not enabled for the database.
2019-07-24T22:44:43.041+0000 I CONTROL  [initandlisten] **          Read and write access to data and configuration is unrestricted.
2019-07-24T22:44:43.041+0000 I CONTROL  [initandlisten] 
---
Enable MongoDB's free cloud-based monitoring service, which will then receive and display
metrics about your deployment (disk utilization, CPU, operation statistics, etc).

The monitoring data will be available on a MongoDB website with a unique URL accessible to you
and anyone you share the URL with. MongoDB may use this information to make product
improvements and to suggest MongoDB products and deployment options to you.

To enable free monitoring, run the following command: db.enableFreeMonitoring()
To permanently disable this reminder, run the following command: db.disableFreeMonitoring()
---

> use control_system
switched to db control_system
> db.logs.find()
{ "_id" : ObjectId("5d38df5d93196eae5e734b46"), "log_level" : 6, "event" : "\n        Fan controller established the connection to Mongo:\n        host => 172.99.0.12 ;\n        port => 27017 ;\n        db => control_system ;\n        collection => logs", "timestamp_utc" : "2019-07-24 22:44:45.763566" }
{ "_id" : ObjectId("5d38df5d2c0cf87d86c901e3"), "log_level" : 6, "event" : "\n        Data manager established the connection to Mongo:\n        host => 172.99.0.12 ;\n        port => 27017 ;\n        db => control_system ;\n        collection => logs", "timestamp_utc" : "2019-07-24 22:44:45.771589" }
{ "_id" : ObjectId("5d38df5d93196eae5e734b47"), "log_level" : 6, "event" : "\n        Fan controller established the connection to Redis;\n        host => 172.99.0.10 ;\n        port => 6379 ;\n        db => 0", "timestamp_utc" : "2019-07-24 22:44:45.775797" }
{ "_id" : ObjectId("5d38df5d2c0cf87d86c901e4"), "log_level" : 6, "event" : "\n        Data manager established the connection to Redis;\n        host => 172.99.0.10 ;\n        port => 6379 ;\n        db => 0", "timestamp_utc" : "2019-07-24 22:44:45.775857" }
{ "_id" : ObjectId("5d38df5d2c0cf87d86c901e5"), "log_level" : 6, "event" : "\n        Data manager established the connection to Postgres:\n        host => 172.99.0.11 ;\n        user => postgres ;\n        dbname => control_system", "timestamp_utc" : "2019-07-24 22:44:45.780404" }
{ "_id" : ObjectId("5d38df5d93196eae5e734b48"), "log_level" : 6, "event" : "\n        Fan controller established the connection to Postgres:\n        host => 172.99.0.11 ;\n        user => postgres ;\n        dbname => control_system", "timestamp_utc" : "2019-07-24 22:44:45.780659" }
{ "_id" : ObjectId("5d38df5e2c0cf87d86c901e6"), "log_level" : 6, "event" : "\n                A new subsystem, SUBSYS-1000, registered and its info. got stored in Postgres", "timestamp_utc" : "2019-07-24 22:44:46.546722" }
{ "_id" : ObjectId("5d38df5e2c0cf87d86c901e7"), "log_level" : 6, "event" : "\n                Subsystem, SUBSYS-1000, reports its temperature 98", "timestamp_utc" : "2019-07-24 22:44:46.551454" }
{ "_id" : ObjectId("5d38df5f2c0cf87d86c901e8"), "log_level" : 6, "event" : "\n                A new subsystem, SUBSYS-2000, registered and its info. got stored in Postgres", "timestamp_utc" : "2019-07-24 22:44:47.217145" }
{ "_id" : ObjectId("5d38df5f2c0cf87d86c901e9"), "log_level" : 6, "event" : "\n                Subsystem, SUBSYS-2000, reports its temperature 13", "timestamp_utc" : "2019-07-24 22:44:47.221632" }
{ "_id" : ObjectId("5d38df612c0cf87d86c901ea"), "log_level" : 6, "event" : "\n                Subsystem, SUBSYS-1000, reports its temperature 95", "timestamp_utc" : "2019-07-24 22:44:49.560463" }
{ "_id" : ObjectId("5d38df622c0cf87d86c901eb"), "log_level" : 6, "event" : "\n                Subsystem, SUBSYS-2000, reports its temperature 96", "timestamp_utc" : "2019-07-24 22:44:50.227959" }
{ "_id" : ObjectId("5d38df6293196eae5e734b49"), "log_level" : 6, "event" : "\n                        Controller sent control signal to the FAN-1000 with adjusted speend 100", "timestamp_utc" : "2019-07-24 22:44:50.759499" }
{ "_id" : ObjectId("5d38df6393196eae5e734b4a"), "log_level" : 6, "event" : "\n                        Controller sent control signal to the FAN-2000 with adjusted speend 100", "timestamp_utc" : "2019-07-24 22:44:51.065855" }
{ "_id" : ObjectId("5d38df6393196eae5e734b4b"), "log_level" : 6, "event" : "\n                        Controller sent control signal to the FAN-3000 with adjusted speend 100", "timestamp_utc" : "2019-07-24 22:44:51.371456" }
{ "_id" : ObjectId("5d38df642c0cf87d86c901ec"), "log_level" : 6, "event" : "\n                Subsystem, SUBSYS-1000, reports its temperature 60", "timestamp_utc" : "2019-07-24 22:44:52.570915" }
{ "_id" : ObjectId("5d38df652c0cf87d86c901ed"), "log_level" : 6, "event" : "\n                Subsystem, SUBSYS-2000, reports its temperature 1", "timestamp_utc" : "2019-07-24 22:44:53.236929" }
{ "_id" : ObjectId("5d38df6593196eae5e734b4c"), "log_level" : 6, "event" : "\n                        Controller sent control signal to the FAN-1000 with adjusted speend 76.0", "timestamp_utc" : "2019-07-24 22:44:53.683611" }
{ "_id" : ObjectId("5d38df6593196eae5e734b4d"), "log_level" : 6, "event" : "\n                        Controller sent control signal to the FAN-2000 with adjusted speend 76.0", "timestamp_utc" : "2019-07-24 22:44:53.991128" }
{ "_id" : ObjectId("5d38df6693196eae5e734b4e"), "log_level" : 6, "event" : "\n                        Controller sent control signal to the FAN-3000 with adjusted speend 76.0", "timestamp_utc" : "2019-07-24 22:44:54.297974" }
Type "it" for more
> 
...
```

Check config. data in Postgres
```sh
$ docker exec -it isi_robot_system_postgres sh
/ # psql -U postgres control_system
psql (12beta2)
Type "help" for help.

control_system=# \d
                       List of relations
 Schema |              Name              |   Type   |  Owner   
--------+--------------------------------+----------+----------
 public | configuration_fan              | table    | postgres
 public | configuration_fan_id_seq       | sequence | postgres
 public | configuration_subsystem        | table    | postgres
 public | configuration_subsystem_id_seq | sequence | postgres
(4 rows)

control_system=# SELECT * FROM configuration_subsystem;
 id |   comp_id   |     ip     | port |             tstz              
----+-------------+------------+------+-------------------------------
  1 | SUBSYS-1000 | 172.99.1.1 | 8000 | 2019-07-24 22:44:46.546722+00
  2 | SUBSYS-2000 | 172.99.1.2 | 8000 | 2019-07-24 22:44:47.217145+00
(2 rows)

control_system=# SELECT * FROM configuration_fan;
 id | comp_id  |     ip     | port |             tstz              
----+----------+------------+------+-------------------------------
  1 | FAN-1000 | 172.99.2.1 | 8000 | 2019-07-24 22:44:49.02646+00
  2 | FAN-2000 | 172.99.2.2 | 8000 | 2019-07-24 22:44:49.722714+00
  3 | FAN-3000 | 172.99.2.3 | 8000 | 2019-07-24 22:44:50.301133+00
(3 rows)

control_system=#
```

Read data stored in Redis
```sh
$ docker exec -ti isi_robot_system_redis sh
/data # 
/data # 
/data # 
/data # 
/data # 
/data # redis-cli 
127.0.0.1:6379> KEYS *
1) "SUBSYS"
2) "SUBSYS-1000"
3) "SUBSYS-2000"
127.0.0.1:6379> HGET SUBSYS-1000 TEMPERATURE
"10"
127.0.0.1:6379> 
```
