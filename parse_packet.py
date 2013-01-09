def process_packet(header, data):
	print "Header: "+header
	print "Data: "+data

	source_callsign = ""
	destination_callsign = ""

	#Check the first character if the data and decide what to do,
	#according to the APRS Data Type Identifier table, page 27, APRS101.pdf
	
	#If it is a relayed packet the source callsign is in the data and 
	#not in the header.
	if(data[0] == '}'):
		source_callsign = data[1:(data.find('>'))] #Extract the source from the embedded header
		data = data[(data.find(':')+1):] #The data follows the embedded header
		
	else:
		source_callsign = header[3:(header.find("to")-1)] #Extract the source from the real header
		#The data remains the same
		
	print "Source: "+source_callsign
	print "RData: "+data
