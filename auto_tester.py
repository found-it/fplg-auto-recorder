#
#   File:       auto_tester.py
#   Authors:    Hassan Al Ajmi <hl515012@gmail.com>
#               James Petersen <jpetersenames@gmail.com>
#
#   This is the Python script that runs the auto testing
#   rig built by the senior design team of the 2017-2018
#   school year.
#

#!/usr/bin/python

# Imports..................
from   ctypes import *
from   sys    import argv
import RPi.GPIO as g
import datetime
import serial
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

# script argument stuff
print argv
if len(argv) > 1:
    print len(argv)
    print argv[1]

# Open up SPI
spi = spidev.SpiDev()
spi.open(0,0)

# Get the VL6180 C functions
vl = CDLL('./vl6180/vl6180.so')

# Get the TMP007 C functions
tm = CDLL('./tmp007/tmp007.so')


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


# This function returns the oversampled
# current value from the ACS712
def get_current(channel):
    acs_offset = 2.438
    acs_step   = 0.185
    reading = 0
    for i in xrange(63):
        reading = reading + get_adc(channel)
    reading  = reading>>6
    adc_volt = adc_to_volt(reading)
    adj_volt = adc_volt - acs_offset
    current  = adj_volt / acs_step
    return current


# This function returns the 10-bit integer
# received from the ADC.
def get_adc(channel):
    if ((channel > 7) or (channel < 0)):
        return ERROR
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
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
try:
    # This function reads from rs232 
    if (force_on):
        ser = serial.Serial(
            port     = '/dev/ttyUSB0',
            baudrate = 19200,
            parity   = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout  = 1
        )
        print "Opening " + str(ser.name) + " for load cell communication."

    # Initialize the VL6180
    vl6180_fd = init_vl6180()

    # Initialize the TMP007 and set up for Python use
    tmp007_fd   = tm.tmp007_setup()
    tmp007_read = tm.tmp007_read_temp
    tmp007_read.restype = c_float

    # Get the time and create file name
    timestr = time.strftime("%m-%d-%y_%H-%M-%S")
    filename = "tests/" + timestr + "_test.csv"

    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Current [A]', 'Voltage [V]', 'Distance [mm]', 'Temperature [C]', 'Force [Units]'])

        while True:

            # Get the measurements
            acs_current = get_current(current_channel)
            volt        = get_voltage(voltage_channel)
            dist        = vl.vl6180_read_range(vl6180_fd)
            temp        = float(tmp007_read(tmp007_fd))
            time        = str(datetime.datetime.now().time())
            if (force_on):
                force       = ser.readline()
                mylist = force.split()
                print mylist[0]
                print mylist[1]
                print mylist[2]
                csv_w.writerow([time, acs_current, volt, dist, temp, force])
                print "force:       " + str(force) + " N"
            # Write to csv
            else:
                csv_w.writerow([time, acs_current, volt, dist, temp, "force"])


            print "time:        " + time
            print "distance:    " + str(dist)  + " mm"
            print "temperature: " + str(temp)  + " C"
            print "voltage:     " + str(volt)  + " V"
            print "current:     " + str(acs_current)  + " V"
            print "-------------------"

# Close up the spi..
finally:
    spi.close()
    g.cleanup()
