from ctypes import *
import RPi.GPIO as g
import time
import datetime
import csv

vl = CDLL('./vl6180.so')

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

csv_write = False

try:
    fd = init_vl6180()
    if csv_write:
        filename = "vl6180_sampling_rate_new.csv"
        with open(filename, 'wb') as outfile:
            csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_w.writerow(['Time (h:m:s)', 'Distance [mm]'])

            while True:

                # Get the measurements
                # Write to csv
                time = str(datetime.datetime.now().time())
                dist = vl.vl6180_read_range(fd)
                csv_w.writerow([time, dist])
    else:
        vl.vl6180_setup_poll(fd)
        while True:
            if vl.vl6180_poll(fd) == 0x04:
                dist = vl.vl6180_read(fd)
                print "dist: " + str(dist)
                vl.vl6180_setup_poll(fd)
            print "do other stuff"


except KeyboardInterrupt:
    print "Ended\n"
finally:
    print "Cleaning up..."
    g.cleanup()
