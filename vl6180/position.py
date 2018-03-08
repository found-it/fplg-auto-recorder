from ctypes import *
import RPi.GPIO as g
from time import sleep

try:
    gpin = 21
    print "setting up pin " + str(gpin)
    g.setmode(g.BCM)
    g.setup(gpin, g.OUT)
    print "Toggling shdn pin"
    g.output(gpin, 0)
    sleep(0.1)
    g.output(gpin, 1)

    vl = CDLL('./vl6180.so')
    fd = vl.vl6180_setup()
    while(1):
        print vl.vl6180_read_range(fd)

except KeyboardInterrupt:
    print "Ended\n"
finally:
    print "Cleaning up..."
    g.cleanup()
