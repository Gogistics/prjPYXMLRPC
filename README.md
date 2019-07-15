# Design of Control Systems for monitoring the fan cluster

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

## Architecture diagram (WIP)
This section is about the [architecture of the robot's systems](https://drive.google.com/file/d/17PLyc8d8U6ONpMeFGOvlmbNnkhTWT-kN/view?usp=sharing). Basically, the diagram comprises of the relationship between all the mechanisms and the network design. The architecture is designed in the fasion of microservices.

#### Control system
In modern control theory, observability and controllability are crucial factors of a system; roughly speaking, a control system needs inputs from the measurement mechanism and then generates outputs to move a system to the desired states. In this coding task, the control system is designed to configure all the subsystems and the fan controllers by app_config_handler, collect the temperatures of all the subsystems by app_data_collector, and send control signals to fan controllers by app_fan_controller. As for the databases, each type of databases only has an instance instead of master-slave cluster; for production services, it is recommended to have a setup of master-slave cluster because master node is for handling **write** operation and all slave nodes are for **read** operation.

All applications run inside Docker containers for demo/testing purpose.

* Application of handling configuration
  The control application can be simulated by XMLRPC server or Flask.

* Application of handling state reports from subsystems
  The control application can be simulated by XMLRPC server or Flask.

* Application of sending control signals to all fans' controllers
  The control application can be simulated by XMLRPC server or Flask.

* Redis
  In-memory database is used to store the temporary state data of all the subsystems

* Postgres
  SQL database is for storing the configuration data of all the subsystems and the fan controllers

* Mongo
  NoSQL databases is for storing log data


#### Subsystems (WIP)
* Application of reporting the temperature of the subsystem and logs to control system

#### Fan systems (WIP)

#### Network design
In this coding task, there is only one network, **172.99.0.0/16**.


---

## Code implementation (WIP)

#### Explanation of the project directory

* control_system
This directory contains all stuff for bringing up a control system.

* subsystems
This directory contains all stuff for bringing up all subsystems.

* fans
This directory contains all stuff for bringing up all fan systems.

---

## Testing (WIP)

#### How to run tests
