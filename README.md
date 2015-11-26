OnionDoor
=========

The OnionDoor script runs on a RaspberryPi in the Berlin ZweibelRaum
office. Currently the script simply opens the door in response to a
buzzer press. A more complex access control policy is planned for the
future.

The door system is a Ritto TwinBus system with a handset and door open
button in the office. The RaspberryPi interfaces to the buzzer and open
push button via two opto-isolators and a current limiting circuit.

Installation
------------

This script uses the RPi.GPIO python library for interfacing with the
RaspberryPi GPIO pins. This library is shipped with the current version
of Raspbian.

    sudo python setup.py install
    sudo cp oniondoor.service /etc/systemd/system/oniondoor.service
    sudo systemctl enable oniondoor.service

Tor should be configured to forward http traffic to the webserver on
port 5000. iptables rules need to be configured to forward local requests
on port 80.

    iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 5000
    iptables -t nat -I OUTPUT -p tcp -o lo --dport 80 -j REDIRECT --to-ports 5000

OnionDoor will look for a config file at:

    /usr/var/oniondoor.main-instance/config.py


RaspberryPi Pinout
------------------

![GPIO Pinout](/images/gpio-pinout.png)


Circuit Schematic
-----------------

TOOD
