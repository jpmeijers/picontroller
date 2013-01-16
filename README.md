PiController
============

APRS repeater controller running on a Raspberry Pi and written in Python.

This program switches GPIO pins on or off on the Raspberry Pi's P1 header
according to commands received over APRS. APRS is received via a transceiver
plugged in an USB soundcard attached to the Pi. A soundcard modem then
demodulates the AFSK1200 signal which is read in and parsed by this program.


WARNING
=======

This program is meant for Amateur radio use. If you do not have the required
radio frequency license, do not use this program.

This program writes config files for soundmodem and ax25tools in
  /etc/ax25/soundmodem.conf  and  /etc/ax25/axports
  
If any of these two files exist when PiController is started up,
they will be overwritten. Backup your old config files before running
PiCOntroller.


Prerequisites
=============

Raspberry Pi running Raspbian OS.

Install the following two packages:
sudo apt-get install soundmodem ax25-tools

A USB soundcard. During testing a Logitech one was used and Raspbian already
had the appropriate drivers.

Soundcard interface with VOX circuit. Plans for a simple one that was used as 
basis for the testing setup can be found at: http://www.g4ilo.com/usblink.html


Set up
======

Open picontroller.conf and modify the settings to suite you. Pay careful 
attention to the my\_callsign and my\_location settings.

Connect a radio and check your soundcard audio levels with 
soundcardmodem-config. Make sure you are using a frequency you are licensed to
use and that is meant for APRS or packet use according to your country's
Amateur radio band plan.

When all is set up you can run the program by executing the following line
in a terminal:
sudo python picontroller.py

As this application calls soundmodem, which creates a new network interface, 
and this application controls GPIO pins, you need to run it as a super user.


Usage
=====

The system will periodically send out a beacon containing a description
and the location of the controller. The description, location and frequency
of the beacon can be set in the config file.

To force the system to send out a beacon, an authorised user (list of authorised
users specified in config file) can send a APRS message to the controller. For 
a beacon the message should either contain only a "B" or the word "BEACON". 
Commands are case insensitive.

To get the status of GPIO inputs and outputs, a message containing "G" or "GET"
must be sent to the controller. It will then reply with a message listing 
inputs, their statusses, followed by outputs and their statusses. 

To set the status of GPIO outputs, a message starting with "S" or "SET" must be
sent to the controller. This command must be followed by a space, then a comma 
seperated list of port-status pairs. For example:
  SET A0,B1,C0
This example will switch port A and C on, and switch port B off. This command
and port names are also case-insensitive. 
