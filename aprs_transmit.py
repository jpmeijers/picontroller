import pprint
import subprocess
import time
import random

#own classes
import gpio_management

packet_counter = 1

def init():
	global packet_counter
	packet_counter = 1

def send_beacon(config):
	#beacon -c ZS1JPM-6 -d "BEACON WIDE1-1" -s sm0 "=3357.92S/01850.19E#JP in technopark"
	location = config.get("APRS encoding", "my_location")
	location = location.split(",")
	latitude = float(location[0])
	longitude = float(location[1])
	latDeg = int(latitude)
	lonDeg = int(longitude)
	latMin = abs(latitude-latDeg)*60
	lonMin = abs(longitude-lonDeg)*60
	
	latDir = "N"
	if (latDeg<0): latDir = "S"
	lonDir = "E"
	if (lonDeg<0): lonDir = "W"
	
	latFull = "%2d%2.2f%s" % (abs(latDeg),latMin,latDir)
	#print latFull
	
	lonFull = "%03d%2.2f%s" % (abs(lonDeg),lonMin,lonDir)
	#print lonFull
	
	send_packet(config, "="+latFull+config.get("APRS encoding", "my_symbol_table")
						+lonFull+config.get("APRS encoding", "my_symbol_object")
						+config.get("APRS encoding", "my_name"))


def send_current_state(config,source_callsign, source_ssid):
	input_states = gpio_management.get_input_states(config)
	output_states = gpio_management.get_output_states_from_cache(config)
	reply_message = "IN "
	
	for i in input_states:
		reply_message += i.upper()+","
	reply_message = reply_message.rstrip(",")
	
	reply_message += " OUT "
	for o in output_states:
		reply_message += o.upper()+","
	reply_message = reply_message.rstrip(",")
	
	#TODO: temperature sensor
	
	send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":STATUS "+reply_message+" END")


def send_message(config, message_text):
	
	global packet_counter
	send_packet(config, message_text+"{%d" % packet_counter)
	
	if(packet_counter<99999):
		packet_counter+=1
	else:
		packet_counter=1
		

def send_packet(config, message_text):
	#works, but just give a second delay first
	time.sleep(1)
	time.sleep(random.random()*2)
	
	subprocess.call(["beacon -c "+config.get("APRS encoding", "my_callsign")
		+" -d "+config.get("APRS encoding", "beacon_path")
		+" -s "+config.get("soundmodem", "sm_interface")
		+" \""+message_text+"\""], shell=True)
	print ("Packet sent: "+message_text)
	

