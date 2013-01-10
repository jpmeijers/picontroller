def switch_output(config, name, state):
	#Switch one outpu on or off
	
	#Check if name is a defined GPIO
	return 0 #invalid GPIO name
	
	#Check if name is a output
	return 0 #not an output
	
	return 1 #on success
	
	
def switch_list(config, name_list):
	#switch a list of outputs on or off
	for (i in name_list):
		if(switch_output(i[0], i[1]) != 1):
			return 0
	
	
def get_input_states(config):
	#return a list of all inputs and their values
	
	#port_list = 
	#state_list = None
	
	#for (port in port_list):
	#	state_list.add port
	
	#return state_list
	pass
	
