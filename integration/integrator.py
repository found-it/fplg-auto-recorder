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
top_voltage_channel = 0
bot_voltage_channel = 1
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
printd = False
try:
    # Get the time and create file name
    timestr = time.strftime("%m-%d-%y_%H-%M-%S")
    filename = "../tests/" + timestr + "_test.csv"

    # Initialize the VL6180
    vl6180_fd = init_vl6180()

    t1 = datetime.datetime.now()
    v1t = get_voltage(top_voltage_channel)
    v1b = get_voltage(bot_voltage_channel)
    trapzt = (vl.vl6180_read_range(vl6180_fd)) / 1000
    trapzb = trapzt
    cnt = 0
    dist = 0
    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Voltage Top [V]', 'Voltage Bot [V]', 'Position due to Integration Top', 'Position due to Integration Bot', 'Distance [mm]'])
        while True:
            t2 = t1
            v2t = v1t
            v2b = v1b
            timen = str(datetime.datetime.now().time())
            v1t = get_voltage(top_voltage_channel)
            v1b = get_voltage(bot_voltage_channel)
            t1 = datetime.datetime.now()
            dt = (t1 - t2).total_seconds()
            trapzt = (dt/2) * (v1t + v2t + 2*trapzt)
            trapzb = (dt/2) * (v1b + v2b + 2*trapzb)

            if cnt == 0:
                dist = vl.vl6180_read_range(vl6180_fd)
                csv_w.writerow([timen, v1t, v1b, trapzt, trapzb, dist])
                cnt = 0
            else:
                csv_w.writerow([timen, v1t, v1b, trapzt, trapzb])
            cnt = 0

            if printd:
                print "distance: " + str(dist)  + " mm"
                print "time:   " + timen
                print "dt:     " + str(dt)
                print "v1t:    " + str(v1t)  + " V"
                print "v1b:    " + str(v1b)  + " V"
                print "trapzb: " + str(trapzb) + " mm"
                print "trapzt: " + str(trapzt) + " mm"
                print "-------------------"
#                time.sleep(0.1)
#            cnt += 1

# Close up the spi..
finally:
    spi.close()
    g.cleanup()
