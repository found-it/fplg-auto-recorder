#
#   File:       auto_tester.py
#   Authors:    Hassan Al Ajmi <email>
#               James Petersen <jpetersenames@gmail.com>
#
#   This is the Python script that runs the auto testing
#   rig built by the senior design team of the 2017-2018
#   school year.
#

# Imports
from time   import sleep
from ctypes import *
import spidev
import RPi.GPIO as g

# Variables
acs_offset = 2.438
acs_step   = 0.185

# Open up SPI
spi=spidev.SpiDev()
spi.open(0,0)

# Get the VL6180 C functions
vl = CDLL('./vl6180/vl6180.so')

# This function returns the 10-bit integer
# received from the ADC.
def get_adc(channel):
    if ((channel > 1) or (channel < 0)):
        return -1
    r = spi.xfer2([1,(2+channel)<<6,0])
    ret = ((r[1]&31) << 6) + (r[2] >> 2)
    return ret


# This function returns the converted
# adc voltage
def adc_to_volt(reading):
    return float((reading*3.3)/1024)


# This function returns the oversampled
# current value from the ACS712
def get_current():
    reading = 0
    for i in xrange(127):
        reading = reading + get_adc(0)
    reading = reading>>7
    a2d_volt = adc_to_volt(reading)
    adj_volt = (a2d_volt - acs_offset)
    cur = adj_volt / acs_step
    print "Reading:     ", reading
    print "A2D Voltage: ", a2d_volt
    print "Adjust Volt: ", adj_volt
    print "Current:     ", cur
    print "---------------------"
    return cur


# This function initializes the VL6180 sensor.
# It returns the file descriptor that is needed
# to pass into the vl6180_read_range(file_descriptor)
# function.
def init_vl6180():
    gpin = 21
    print "Setting up pin " + str(gpin)
    g.setmode(g.BCM)
    g.setup(gpin, g.OUT)
    print "Toggling shdn pin"
    g.output(gpin, 0)
    sleep(0.1)
    g.output(gpin, 1)
    return vl.vl6180_setup()

# Main loop.........
try:
    vl6180_fd = init_vl6180()
    while True:
        #        sleep(0.5)
        print str(vl.vl6180_read_range(vl6180_fd)) + "mm"
#        acs_current = get_current()

# Close up the spi..
finally:
    spi.close()
    g.cleanup()
