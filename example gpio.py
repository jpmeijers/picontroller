import RPi.GPIO as GPIO
import time

# to use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)

GPIO.cleanup()

# set up GPIO output channel
GPIO.setup(12, GPIO.OUT)

# set RPi board pin 12 high
GPIO.output(12, GPIO.HIGH)

# set up GPIO input with pull-up control
#   (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

# input from RPi board pin 11
input_value = GPIO.input(11)

# set up rising edge detection (EXPERIMENTAL)
GPIO.set_rising_event(11)

#print "Waiting for an event"

# set up falling edge detection (EXPERIMENTAL)
#GPIO.set_rising_event(11, enable=False)  # disable rising edge detection (as set above)
#GPIO.set_falling_event(11)

# set up high detection (EXPERIMENTAL)
#GPIO.set_falling_event(11, enable=False)  # disable falling edge detection (as set above)
#GPIO.set_high_event(11)

# set up low detection (EXPERIMENTAL)
#GPIO.set_high_event(11, enable=False)  # disable high detection (as set above)
#GPIO.set_low_event(11)

# check for an event (EXPERIMENTAL)
#if GPIO.event_detected(11):
#    print('Rising edge detected!')

# to change to BCM GPIO numbering
#GPIO.setmode(GPIO.BCM)

while True:
	if input_value != GPIO.input(11):
		print "Pin 11 state changed."
		input_value = GPIO.input(11)
	time.sleep(1)

# to reset every channel that has been set up by this program to INPUT with no pullup/pulldown and no event detection.
GPIO.cleanup()
