#!/usr/bin/python
import ConfigParser
import signal
import subprocess
import shutil
import sys
import parse_packet
import gpio_management

#global variables
sm_process = None
axlisten_process = None


#load config file
config = ConfigParser.ConfigParser()
config.read(['picontroller.conf'])

#Program exit
def exit_handler(signal, frame):
	global sm_process
	global axlisten_process
	
	print '\nCtrl+C pressed, system exiting.'
	#close all running threads and open files
	
	gpio_management.deinit()
	sm_process.terminate()
	axlisten_process.terminate()
	
	sys.exit()
signal.signal(signal.SIGINT, exit_handler)


def write_sm_ax_configs():
	shutil.copyfile('./soundmodem.conf', '/etc/ax25/soundmodem.conf')
	shutil.copyfile('./axports', '/etc/ax25/axports')


def start_soundmodem():
	global sm_process
	sm_process = subprocess.Popen(["soundmodem"])

def start_axlisten():
	global axlisten_process
	axlisten_process = subprocess.Popen(["axlisten",config.get('soundmodem','sm_interface')], stdout=subprocess.PIPE)
	
	#read axlisten's output indefinitely
	header = ""
	data_buffer = ""
	packet_length = 0
	while True:
		data = axlisten_process.stdout.readline()
		
		if (data.find(config.get('soundmodem','sm_interface')+": ") == 0):
			header = data.lstrip(config.get('soundmodem','sm_interface')+": ").rstrip("\n")
			position = header.rfind("len ")
			packet_length = int(header[(position+4):].strip())
			#print "\nNew packet of length %d" % packet_length
		
		elif (packet_length != 0):
			data_buffer += data[6:].strip("\n")
			#print data
			if(len(data_buffer) >= packet_length):
				parse_packet.process_packet(config, header, data_buffer)
				#do something with the received data
				
				#Now clear the buffers
				header = ""
				data_buffer = ""
				packet_length = 0
				


#Entry point
if __name__ == "__main__":
	#try:
		write_sm_ax_configs()
		gpio_management.init_gpio(config)
		
		#test case
		#gpio_management.update_cache("A","0")
		
		start_soundmodem()
		start_axlisten()
		
		exit_handler(None,None)
	#except:
		#exit_handler(None,None)
		#pass
