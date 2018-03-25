#
#   File:       auto_tester.py
#   Authors:    Hassan Al Ajmi <hl515012@gmail.com>
#               James Petersen <jpetersenames@gmail.com>
#
#   This is the Python script that runs the auto testing
#   rig built by the senior design team of the 2017-2018
#   school year.
#

# Imports
#from oauth2client.service_account import ServiceAccountCredentials
#import gspread
import time
from   ctypes import *
import spidev
import RPi.GPIO as g
import datetime
import serial
import time
import csv
from sys import argv

# Variables
acs_offset = 2.438
acs_step   = 0.185
row        = 1
time_col   = 1
dist_col   = 2
curnt_col  = 3
temp_col   = 4

print argv
if len(argv) < 1:
    print len(argv)
    print argv[1]

# Open up SPI
spi=spidev.SpiDev()
spi.open(0,0)

# Get the VL6180 C functions
vl = CDLL('./vl6180/vl6180.so')

# Get the TMP007 C functions
tm = CDLL('./tmp007/tmp007.so')

# use creds to create a client to interact with the Google Drive API
#scope = ['https://spreadsheets.google.com/feeds']
#creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
#client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
#sheet = client.open("autotest").sheet1

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
    return float((reading*5.0)/1024)

def get_voltage():
    reading = 0
    for i in xrange(7):
        reading = reading + get_adc(1)
    reading = reading>>3
    return adc_to_volt(reading)


# This function returns the oversampled
# current value from the ACS712
def get_current():
    reading = 0
    for i in xrange(7):
        reading = reading + get_adc(0)
    reading = reading>>3
    a2d_volt = adc_to_volt(reading)
    adj_volt = (a2d_volt - acs_offset)
    cur = adj_volt / acs_step
    #print "Reading:     ", reading
    #print "A2D Voltage: ", a2d_volt
    #print "Adjust Volt: ", adj_volt
    #print "Current:     ", cur
    #print "---------------------"
    return cur


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
#    ser = serial.Serial(
#        port='/dev/ttyUSB0',
#        baudrate = 19200,
#        parity=serial.PARITY_NONE,
#        stopbits=serial.STOPBITS_ONE,
#        bytesize=serial.EIGHTBITS,
#        timeout=1
#    )
#    counter=0


    vl6180_fd = init_vl6180()

    tmp007_fd = tm.tmp007_setup()
    tmp007_read = tm.tmp007_read_temp
    tmp007_read.restype = c_float

#    sheet.update_cell(row, time_col,  "Time (h:m:s)")
#    sheet.update_cell(row, dist_col,  "Distance (mm)")
#    sheet.update_cell(row, curnt_col, "Current (A)")
#    sheet.update_cell(row, temp_col,  "Temperature (C)")

    timestr = time.strftime("%m-%d-%y_%H-%M-%S")
    print timestr
    filename = "tests/" + timestr + "_file.csv"

    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Current [A]', 'Voltage [V]', 'Distance [mm]', 'Temperature [C]', 'Force [Units]'])
        while True:
            acs_current = get_current()
            volt        = get_voltage()
            dist        = vl.vl6180_read_range(vl6180_fd)
            temp        = float(tmp007_read(tmp007_fd))
            time        = str(datetime.datetime.now().time())
            csv_w.writerow([time, acs_current, volt, dist, temp, "force"])

            # Get the distance measurement
#            print "distance:      " + str(dist)   + " mm"
#            print "temperature:   " + str(temp)   + " C"
#            print "voltage:       " + str(volt)   + " V [regulated]"
#            print "voltage [tot]: " + str(volt*5) + " V [actual]"
#            print "-------------------"

        # Increment the row 
#        x=ser.readline()
#        print x
#        row += 1
        # Update the sheet

#sheet.update_cell(row, time_col, str(datetime.datetime.now().time()))
#sheet.update_cell(row, curnt_col, acs_current)
#sheet.update_cell(row, dist_col, dist)
#sheet.update_cell(row, temp_col, temp)






# Close up the spi..
finally:
    spi.close()
    g.cleanup()
