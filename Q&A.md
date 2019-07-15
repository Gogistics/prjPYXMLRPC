# Questions
All questions about the coding task are listed here and the answered questions will be striked through. 

1. Are there certain relationship between subsystems and fans?
For example, the system has 5 subsystems and 3 fans
* fan-1 can cool down subsystem-1 and subsystem-4
* fan-2 can cool down subsystem-2, subsystem-3, and subsystem-5
* fan-3 can cool down subsystem-1 and subsystem-3

Based on my knowledge about modern control, a system is better to be observable and controllable in a closed loop. According to the problem statement and requirements, I don't see the relationship between temperature and fan speed, which means it is impossible to measure the temperature change when the fan speed changes and approve the control algorithm works properly.

Ans: NA

---

2. I'm confused about the requirements:
Application requirement-
**The maximum speed may be different for different fans. ...**

Control algorithm requirements-
**... the fan max speed should be computed from the maximum of the most recent temperatures of all subsystems.**
**All fans should be set to the same percentage of max speed.**

Are the max speed of the fans the same or not?

Ans: NA

---

3. **The number of subsystems and the number of fans present should both be configurable at startup. ...** Does this statement means *the number of subsystems and the number of fans are configurable by a configuration file which is defined by engineers/developers and read by the control system at startup* or *the subsystems and fans are connected to the control system at startup, and the control system auto-configures the subsystems and fans and store the configuration data in the database*?

Ans: NA

---

4. Are the number of subsystems and the number of fans changeable after startup?

Ans: NA

---

5. There is only one network required for all systems of this robot, right?

Ans: NA

---

6. The temperature of a subsystem is measured by a corresponding mechanism which reports the result to the subsystem and each subsystem has same mechanism for doing that work, right?

Ans: NA

---

7. The control system only send the signals to all fans and each fan has a mechanism to fine-tune some internal state variables in order to adjust fan speed, right?

Ans: NA

---

8. The system has to log all system data which include the logs of the control system itself, right?

Ans: NA

---

9. Could systems/applications be simulated by XMLRPC server/client or Flask and running inside Docker containers for demo purpose? I would like to build the communication interfaces with RPC/Web server because, from my experience of developing SD-WAN management server, it is more complicated to manage multiple persistent socket channels and handle the failures.

Ans: NA