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

try:
    filename = "vl6180_sampling_rate_new.csv"
    fd = init_vl6180()
    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Distance [mm]'])

        while True:

            # Get the measurements
            # Write to csv
            time = str(datetime.datetime.now().time())
            dist = vl.vl6180_read_range(fd)
            csv_w.writerow([time, dist])


except KeyboardInterrupt:
    print "Ended\n"
finally:
    print "Cleaning up..."
    g.cleanup()
