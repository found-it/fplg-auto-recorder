#
#   File:       load_cell_sample_rate.py
#   Authors:    Hassan Al Ajmi <hl515012@gmail.com>
#               James Petersen <jpetersenames@gmail.com>
#

#!/usr/bin/python

# Imports..................
import datetime
import serial
import time
import csv

# pseudo defines
ERROR = -1


# Main loop.........
try:
    # This function reads from rs232 
    ser = serial.Serial(
        port     = '/dev/ttyUSB0',
        baudrate = 19200,
        parity   = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout  = 1
    )
    print "Opening " + str(ser.name) + " for load cell communication."

    filename = "load_cell_sample_rate.csv"

    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Force [Units]'])

        while True:

            # Get the measurements
            force       = ser.readline()
            csv_w.writerow([time, force])

# Close up the spi..
finally:
    print "Done!"
