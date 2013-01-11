import pprint

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
	
	#print "Source: "+source_callsign+"-"+source_ssid
	#print "Data: "+data
	#print "\n"
	print ".",
	
	#Is this an APRS message packet? APRS101, p71
	if(data[0] == ':' and data[10] == ':'):
		#This is and APRS message packet.
		#Is it addressed to me? 
		if(data[1:10].find(config.get("APRS encoding","my_callsign")) != -1):
			process_aprs_message(config, source_callsign, source_ssid, data)
			print "-",
	

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
	
		#If authorised, ack, else rej
		if(source_callsign.lower() in list_of_users):
			print "%s is an authorised user" % source_callsign
			send_packet(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":ack"+data[(msg_id_index+1):])

		else:
			print "%s is not an authorised user" % source_callsign
			#send_packet(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":rej"+data[(msg_id_index+1):])
			#The rej packet was not interpreted correctly by APRStracker during testing. It was seen as another
			#message and not a reject. Therefore ACK in this case too to prevent unneccesary retransmits.
			send_packet(config, ":"+(source_callsign+"-"+source_ssid).ljust(9)+":ack"+data[(msg_id_index+1):])
			
		#Now strip the message id
		data = data[:msg_id_index]
		

	#If unauthorised, ignore message further.
	if(source_callsign.lower() in list_of_users):
		pass
	else:
		return

	#TODO: Use the password in the config file to do authentication
	#if authenticated:
	#	pass
	#else:
	#	return
	
	#Remove the callsign from the data
	data = data[11:]
	#Make all caps to be case insensitive
	data = data.upper()
	
	if(data == ""):
		print "Empty message received."
		return
	
	
	#If the message is "GET","get","G" or "g", send a packet with the current 
	#GPIO states.
	if(data.find("GET") == 0 or data.find('G')):
		aprs_transmit.send_current_state(config,source_callsign, source_ssid)
	
	
	#If the message is "SET A1", "S a1", "s A1" or "set a1,b0...", switch the GPIO's and then send
	#the current state.
	elif(data.find("SET") == 0 or data.find('S')):
		data = data.strip("SET")
		data = data.strip("S")
		data = data.strip()
		
		ports = data.split(",")
		
		for port in ports:
			if (len(port)==2):
				if(gpio_management.set_output(config,port[0],port[1])):
					print "Port successfully set: "+port
				else:
					print "Port not set: "+port
			
			else:
				print "Invalid sintax for a port"
		
		aprs_transmit.send_current_state(config,source_callsign, source_ssid)
		
	
	#If the message is "B","b","BEACON","BeaCon",.. send a beacon now.
	elif(data.find("BEACON") == 0 or data.find('B')):
		aprs_transmit.send_beacon(config)


