#
#   File:    current_sampling.py
#   Author:  James Petersen <jpetersenames@gmail.com>
#

# Imports..................
import datetime
import spidev
import time
import csv

#
# pseudo defines
#
ERROR = -1

#
# Variables
#
ADC_vcc         = 5.0
current_channel = 0
csv_on          = True

#
# Open up SPI
#
spi = spidev.SpiDev()
spi.open(0,0)


#
# Print out the parameters for this script
#
def usage():
    print "ADC Supply Voltage:     {0}".format(ADC_vcc)
    print "Current Channel on MCP: {0}".format(current_channel)
    print "Print to CSV:           {0}".format(str(csv_on))


#
# This function returns the converted
# ADC voltage from the 10-bit ADC
#
def adc_to_volt(reading):
    return float((reading * ADC_vcc) / 1024)


#
# This function returns the oversampled
# current value from the ACS712
#
def get_current():
    acs_offset = 2.438
    acs_step   = 0.185
    reading    = get_adc(current_channel)
    adc_volt   = adc_to_volt(reading)
    adj_volt   = adc_volt - acs_offset
    current    = adj_volt / acs_step
    return current


#
# This function returns the 10-bit integer
# received from the ADC.
#
def get_adc(channel):
    if ((channel > 7) or (channel < 0)):
        return ERROR
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

#
# Main loop.........
#
try:
    # Print the parameters
    usage()

    # Get the time and create file name
    start_time = datetime.datetime.now()
    filename = "currents/current-{0}.csv".format(start_time)
    print "Writing all the info to {0}".format(filename)

    # Write to CSV
    if csv_on:
        with open(filename, 'wb') as outfile:
            csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_w.writerow(['Time Delta [S]', 'Current [A]'])

            while True:
                # Get the measurements
                i_sc = get_current()
                time = ((datetime.datetime.now()) - start_time).total_seconds()

                # Write to csv
                csv_w.writerow([time, i_sc])

    # Print to screen
    else:
        while True:
            i_sc = get_current()
            print "Current: {0} [A]".format(i_sc)


#
# Close up the spi..
#
finally:
    spi.close()
