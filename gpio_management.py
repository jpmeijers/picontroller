import RPi.GPIO as GPIO
import pprint

def init_gpio(config):
	#set up gpios
	# to use Raspberry Pi board pin numbers
	GPIO.setmode(GPIO.BOARD)

	GPIO.cleanup()
	
	#set outputs and inputs according to config file
	port_list = config.options("Port mappings")
	
	for port in port_list:
		
		if(config.get('Port directions',port) == "in"):
			# set up GPIO input with pull-up control
			#   (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
			#print "Port "+port+" set to input."
			GPIO.setup(int(config.get('Port mappings',port)), GPIO.IN, pull_up_down=GPIO.PUD_OFF)
			
		if(config.get('Port directions',port) == "out"):
			# set up GPIO output channel
			#print "Port "+port+" set to output."
			GPIO.setup(int(config.get('Port mappings',port)), GPIO.OUT)

	#set outputs to values in cache file
	try:
		cache_file = open("GPIO.state", "r")
		
		for line in cache_file.readlines():
			if(line.find('#')==-1 and line.strip() != "" and len(line.strip()) == 2):
				portName = line[0]
				portState = line[1]
				#print "Cache entry: "+line.strip()
				if(config.get('Port directions',portName) == "out"):
					#should already be set as an output
					#GPIO.setup(int(config.get('Port mappings',portName)), GPIO.OUT)
					#set value
					if(portState == "0"):
						#print "Setting port "+portName+" to OFF."
						GPIO.output(int(config.get('Port mappings',portName)), GPIO.LOW)
					if(portState == "1"):
						#print "Setting port "+portName+" to ON."
						GPIO.output(int(config.get('Port mappings',portName)), GPIO.HIGH)
		
		cache_file.close()
		
	except:
		#this likely means the file does not exist
		pass
		
		
def deinit():
	GPIO.cleanup()
		

def set_output(config, name, state):
	#Switch one output on or off
	
	#Check if name is a defined GPIO
	port_list = config.options("Port mappings")
	if (name in port_list):
		pass
	else:
		return 0 #invalid GPIO name
	
	#Check if name is a output
	if(config.get('Port directions',name) == "out"):
		pass
	else:
		return 0 #not an output
					
	#should already be set as an output
	#GPIO.setup(int(config.get('Port mappings',portName)), GPIO.OUT)
	#set value
	if(state == "0"):
		print "Setting port "+name+" to OFF."
		GPIO.output(int(config.get('Port mappings',name)), GPIO.LOW)
	elif(state == "1"):
		print "Setting port "+name+" to ON."
		GPIO.output(int(config.get('Port mappings',name)), GPIO.HIGH)
	else:
		return 0
	
	#write the output state to the cache
	update_cache(name, state)
	
	return 1 #on success
	
	
def set_output_list(config, name_list):
	#switch a list of outputs on or off
	for i in name_list:
		if(switch_output(i[0], i[1]) != 1):
			return 0
	
	
def get_input_states(config):
	#return a list of all inputs and their values
	
	port_list = config.options("Port mappings") #list of ports, lower cased
	state_list = []
	
	for port in port_list:
		if(config.get('Port directions',port) == "in"):
			port_state = GPIO.input(int(config.get('Port mappings',port)))
			
			if(port_state):
				state_list.append(port.upper()+"1")
			else:
				state_list.append(port.upper()+"0")
	
	return state_list
	

def get_output_states_from_cache(config):
	cache_file = open("GPIO.state", "r")
	states_list = []
	
	for line in cache_file.readlines():
		if(line.find('#')==-1 and line.strip() != "" and len(line.strip()) == 2):
			states_list.append(line.strip())
			
	return states_list


def update_cache(port, state):
	updated = False
	cache_file = open("GPIO.state", "r")
	lines = cache_file.readlines()
	cache_file.close()
	
	#pprint.pprint(lines)
	
	tel = 0
	for line in lines:
		if (line[0]==port):
			print "Updating "+port
			lines[tel] = port+state+"\n"
			updated = True
		tel += 1
			
	if (not updated):
		lines.append(port+state+"\n")

	#pprint.pprint(lines)
	
	cache_file = open("GPIO.state", "w")
	cache_file.writelines(lines)
	cache_file.close()
