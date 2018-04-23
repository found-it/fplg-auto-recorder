#
#   File:    voltage_sampling.py
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
voltage_channel = 1
csv_on          = True

#
# Open up SPI
#
spi = spidev.SpiDev()
spi.open(0,0)


#
# Print the parameters used by this script
#
def usage():
    print
    print "ADC Supply Voltage:     {0}".format(ADC_vcc)
    print "Voltage Channel on MCP: {0}".format(voltage_channel)
    print "Print to CSV:           {0}".format(str(csv_on))


#
# This function returns the converted
# ADC voltage from the 10-bit ADC
#
def adc_to_volt(reading):
    return float((reading * ADC_vcc) / 1024)


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
# This function gets the measured voltage
# from the ADC and returns the converted voltage
#
def get_voltage(channel):
    divisor   = 8.0
    DC_offset = 2.5
    reading = get_adc(channel)
    return ((adc_to_volt(reading) - DC_offset) * divisor)
#    reading = 0
#    for i in xrange(63):
#        reading = reading + get_adc(channel)
#    reading = reading >> 6


#
# Main loop.........
#
try:
    # Print the parameters for this script
    usage()

    # Write to CSV
    if csv_on:
        # Get the time and create file name
        start_time = datetime.datetime.now()
        filename = "voltages/voltage-{0}.csv".format(start_time)
        print "Writing all the info to {0}".format(filename)
        print
        print

        with open(filename, 'wb') as outfile:
            csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_w.writerow(['Time (h:m:s)', 'Voltage [V]'])

            while True:
                # Get the measurements
                volt = get_voltage(voltage_channel)
                time = ((datetime.datetime.now()) - start_time).total_seconds()

                # Write to csv
                csv_w.writerow([time, volt])

    # Print to screen
    else:
        while True:
            volt = get_voltage(voltage_channel)
            print "Voltage: " + str(volt) + " [V]"
            print "---------------------------------"
            time.sleep(0.5)

#
# Close up the spi..
#
finally:
    spi.close()
