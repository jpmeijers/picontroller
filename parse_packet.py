#   Copyright 2013 JP Meijers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pprint

#own classes
import aprs_transmit
import gpio_management

def process_packet(config, header, data):
	#print "RawHeader: "+header
	#print "RawData: "+data

	source_callsign = ""
	source_ssid="0"
	destination_callsign = ""

	#Check the first character if the data and decide what to do,
	#according to the APRS Data Type Identifier table, page 17, APRS101.pdf
	
	#If it is a relayed packet the source callsign is in the data and 
	#not in the header.
	if(data[0] == '}'):
		source_callsign = data[1:(data.find('>'))] #Extract the source from the embedded header
		data = data[(data.find(':')+1):] #The data follows the embedded header
		
	else:
		source_callsign = header[3:(header.find("to")-1)] #Extract the source from the real header
		#The data remains the same
		
	#Strip SSID's from callsign as it does not mean anything on APRS. 
	#It is just another way of specifying a symbol.
	if (source_callsign.find('-') != -1):
		source_ssid = source_callsign[(source_callsign.find('-')+1):]
		source_callsign = source_callsign[:(source_callsign.find('-'))]
	
	print "Source: "+source_callsign+"-"+source_ssid
	print "Data: "+data
	print "\n"
	#print ".",
	
	#Is this an APRS message packet? APRS101, p71
	if(data[0] == ':' and data[10] == ':'):
		#This is and APRS message packet.
		#Is it addressed to me? 
		if(data[1:10].find(config.get("APRS encoding","my_callsign")) != -1):
			process_aprs_message(config, source_callsign, source_ssid, data)
			#print "-",
	

#We have received an APRS message format packet.
def process_aprs_message(config, source_callsign, source_ssid, data):
	
	#Read list of authorised users
	#Note: When reading a list from a config file, the key is  
	#made lower case, while the value is kept intact
	list_of_users = config.options("Authorised users")
	
	#All messages containing a message ID needs to be acked ackording to 
	#the spec, APRS101, p71
	msg_id_index = data.rfind('{')
	if(msg_id_index != -1):	
		aprs_transmit.send_packet(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":ack"+data[(msg_id_index+1):])
			
		#Now strip the message id
		data = data[:msg_id_index]
		
	#Remove the callsign from the data
	data = data[11:]

	#If the message is in the format ":_________:ack#####" it is an ACK
	#for a message we sent. We can ignore this message for now.
	#TODO: mark the packet as acked in a queue of unacked sent messages
	if (data.lower().find("ack") == 0):
		return
	
	if (config.get("Authorisation","enable_auth") == "True"):
		#If unauthorised, ignore message further.
		if(source_callsign.lower() in list_of_users):
			if (config.get("Authorisation","logauth") == "True"):
				file = open(config.get("Authorisation","authlogfilelocation"), 'a')
				file.write("AUTHED USER: "+source_callsign+"-"+source_ssid+"  MSG: "+data+"\n")
				file.close()
		else:
			if (config.get("Authorisation","logauth") == "True"):
				file = open(config.get("Authorisation","authlogfilelocation"), 'a')
				file.write("UNAUTHED USER: "+source_callsign+"-"+source_ssid+"  MSG: "+data+"\n")
				file.close()
				
			#Consider the following line very carefully. Do you really want to send messages on the request of any user?
			#aprs_transmit.send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":Invalid user or password")
			return

	if (config.get("Authorisation","require_password") == "True"):
		#TODO: Use the password in the config file to do authentication
		user_password = config.get("Authorised users",source_callsign.lower())
		if (data.find(user_password) != -1):
			data = data.strip(user_password)
			data = data.strip()
		else:
			aprs_transmit.send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":Invalid user or password")
			return
	
	#Make all caps to be case insensitive
	data = data.upper()
	
	if(data == ""):
		print "Empty message received."
		return
	
	
	#If the message is "GET","get","G" or "g", send a packet with the current 
	#GPIO states.
	if(data.find("GET") == 0 or data.find('G') == 0):
		aprs_transmit.send_current_state(config,source_callsign, source_ssid)
	
	
	#If the message is "SET A1", "S a1", "s A1" or "set a1,b0...", switch the GPIO's and then send
	#the current state.
	elif(data.find("SET") == 0 or data.find('S') == 0):
		data = data.strip("SET")
		data = data.strip("S")
		data = data.strip()
		
		ports = data.split(",")
		
		success = 1
		for port in ports:
			# ERROR codes:
			# 1=success, 2=invalid gpio, 3=not an output, 4=invalid state, 5=invalid syntax
			
			if (len(port)==2):
				return_code = gpio_management.set_output(config,port[0],port[1])
				if(return_code == 1):
					print "Port successfully set: "+port
				else:
					success = return_code
					print "Port not set: "+port
			
			else:
				success = 5
				print "Invalid syntax for a port"
		
		if(success == 1):
			aprs_transmit.send_current_state(config, source_callsign, source_ssid)
		elif(success == 2):
			aprs_transmit.send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":Invalid GPIO specified")
		elif(success == 3):
			aprs_transmit.send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":GPIO not an output")
		elif(success == 4):
			aprs_transmit.send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":Invalid sate specified")
		elif(success == 5):
			aprs_transmit.send_message(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":Invalid syntax")
			
		
	
	#If the message is "B","b","BEACON","BeaCon",.. send a beacon now.
	elif(data.find("BEACON") == 0 or data.find('B') == 0):
		aprs_transmit.send_beacon(config)


