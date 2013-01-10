import pprint

def process_packet(config, header, data):
	#print "Header: "+header
	#print "Data: "+data

	source_callsign = ""
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
	source_callsign = source_callsign[:(source_callsign.find('-'))]
	
	print "Source: "+source_callsign
	print "Data: "+data
	print "\n"
	
	#Is the packet an APRS message packet? APRS101, p71
	#And even more important, is the message addressed to me
	if(data[0] == ':' and data[10] == ':' 
	and data[1:10].find(config.get("APRS encoding","my_callsign"))):
		process_aprs_message(config, source_callsign, data)
	

#We have received an APRS message format packet.
def process_aprs_message(config, source_callsign, data):
	
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
			send_packet(config, source_callsign, ":"+source_callsign.ljust(9)+":ack"+data[(msg_id_index+1):])

		else:
			print "%s is not an authorised user" % source_callsign
			send_packet(config, source_callsign, ":"+source_callsign.ljust(9)+":rej"+data[(msg_id_index+1):])
		
		
	
	#TODO: Use the password in the config file to do authentication
	



def send_packet(config, dest, message_text):
	print ("MSG to: "+dest+" MSG: "+message_text)
