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
from time   import sleep
from ctypes import *
import spidev
import RPi.GPIO as g
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Variables
acs_offset = 2.438
acs_step   = 0.185

# Open up SPI
spi=spidev.SpiDev()
spi.open(0,0)

# Get the VL6180 C functions
vl = CDLL('./vl6180/vl6180.so')

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("autotest").sheet1

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
    gpin = 23
    print "Setting up pin " + str(gpin)
    g.setmode(g.BCM)
    g.setup(gpin, g.OUT)
    print "Toggling shdn pin"
    g.output(gpin, 0)
    sleep(0.1)
    g.output(gpin, 1)
    return vl.vl6180_setup()

# Main loop.........
count= 2
time_col = 1
distance_ = 2
current_sheet = 3

try:
    vl6180_fd = init_vl6180()
    sheet.update_cell(1,1, "Time (h:m:s)")
    sheet.update_cell(1,2, "Distance (mm)")
    sheet.update_cell(1,3, "Current (A)")

    while True:
        sleep(0.5)
        dis=str(vl.vl6180_read_range(vl6180_fd)) 
        print dis
        sheet.update_cell(count, 1,str(datetime.datetime.now().time()))
        sheet.update_cell(count,2, dis)
        
        count+=1
        
        # acs_current = get_current()
    
# Close up the spi..
finally:
    spi.close()
    g.cleanup()
