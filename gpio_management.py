import RPi.GPIO as GPIO

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
			print "Port "+port+" set to input."
			GPIO.setup(int(config.get('Port mappings',port)), GPIO.IN, pull_up_down=GPIO.PUD_OFF)
			
		if(config.get('Port directions',port) == "out"):
			# set up GPIO output channel
			print "Port "+port+" set to output."
			GPIO.setup(int(config.get('Port mappings',port)), GPIO.OUT)

	#set outputs to values in cache file
	try:
		cache_file = open(GPIO.state, "r")
		
		for line in cache_file.readlines():
			if(line.find('#')==-1 and line.strip() != ""):
				portName = line[0]
				portState = line[1]
				
				if(config.get('Port directions',portName) == "out"):
					#should already be set as an output
					#set value
					if(portState == "0"):
						print "Setting port "+portName+" to OFF."
						GPIO.output(int(config.get('Port mappings',port)), GPIO.LOW)
					if(portState == "1"):
						print "Setting port "+portName+" to ON."
						GPIO.output(int(config.get('Port mappings',port)), GPIO.HIGH)
		
		cache_file.close()
		
	except:
		#this likely means the file does not exist
		pass
		
		
def deinit():
	GPIO.cleanup()
		

def set_output(config, name, state):
	#Switch one outpu on or off
	
	#Check if name is a defined GPIO
	return 0 #invalid GPIO name
	
	#Check if name is a output
	return 0 #not an output
	
	#write the output state to the cache
	
	return 1 #on success
	
	
def set_output_list(config, name_list):
	#switch a list of outputs on or off
	for i in name_list:
		if(switch_output(i[0], i[1]) != 1):
			return 0
	
	
def get_input_states(config):
	#return a list of all inputs and their values
	
	port_list = config.options("Port mappings")
	state_list = []
	
	for port in port_list:
		if(config.get('Port directions',port) == "in"):
			port_state = GPIO.input(int(config.get('Port mappings',port)))
		#state_list.add port
	
	#return state_list
	pass
	
def get_output_states_from_cache(config):
	pass
