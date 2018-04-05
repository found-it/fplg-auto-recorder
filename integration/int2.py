#
#   File:       auto_tester.py
#   Author:     James Petersen <jpetersenames@gmail.com>
#

#!/usr/bin/python

# Imports..................
from   ctypes import *
from   sys    import argv
import RPi.GPIO as g
import datetime
import spidev
import time
import csv

# pseudo defines
ERROR = -1

# Variables
ADC_vcc         = 5.0
voltage_channel = 0
current_channel = 1
force_on        = False

# Open up SPI
spi = spidev.SpiDev()
spi.open(0,0)

# Get the VL6180 C functions
vl = CDLL('../vl6180/vl6180.so')


# This function returns the converted
# ADC voltage from the 10-bit ADC
def adc_to_volt(reading):
    return float((reading * ADC_vcc) / 1024)


# This function gets the measured voltage
# from the ADC and returns the converted voltage
def get_voltage(channel):
    reading = 0
    for i in xrange(63):
        reading = reading + get_adc(channel)
    reading = reading>>6
    return (adc_to_volt(reading) * ADC_vcc)



# This function returns the 10-bit integer
# received from the ADC.
def get_adc(channel):
    if ((channel > 7) or (channel < 0)):
        return ERROR
    raw  = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((raw[1] & 3) << 8) + raw[2]
    return data


# This function initializes the VL6180 sensor.
# It returns the file descriptor that is needed
# to pass into the vl6180_read_range(file_descriptor)
# function.
def init_vl6180():
    gpin = 26
    print "Setting up pin " + str(gpin)
    g.setmode(g.BCM)
    g.setup(gpin, g.OUT)
    print "Toggling shdn pin"
    g.output(gpin, 0)
    time.sleep(0.1)
    g.output(gpin, 1)
    return vl.vl6180_setup()


# Main loop.........
printd = True
try:
    # Initialize the VL6180
    vl6180_fd = init_vl6180()

    t1 = datetime.datetime.now()
    v1 = get_voltage(voltage_channel)
    trapz = (vl.vl6180_read_range(vl6180_fd)) / 1000
    cnt = 0
    dist = 0
    while True:
        t2 = t1
        v2 = v1
        timen = str(datetime.datetime.now().time())
        v1 = get_voltage(voltage_channel)
        t1 = datetime.datetime.now()
        dt = (t1 - t2).total_seconds()
        trapz = (dt/2) * (v1 + v2 + 2*trapz)

        dist = vl.vl6180_read_range(vl6180_fd)

        if printd:
            print "distance: " + str(dist)  + " mm"
            print "time:  " + timen
            print "dt:    " + str(dt)
            print "v1:    " + str(v1)  + " V"
            print "v2:    " + str(v2)  + " V"
            print "trapz: " + str(trapz) + " mm"
            print "-------------------"
            time.sleep(0.1)

# Close up the spi..
finally:
    spi.close()
    g.cleanup()
