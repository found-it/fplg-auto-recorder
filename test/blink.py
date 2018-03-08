from time import sleep
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.OUT)
try:
	while 1:

		gpio.output(21, 1)
		sleep(0.1)
		gpio.output(21,0)
		sleep(0.1)
except KeyboardInterrupt:
	gpio.cleanup()
