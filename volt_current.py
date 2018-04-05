#
#   File:       volt_current.py
#   Authors:    Hassan Al Ajmi <hl515012@gmail.com>
#               James Petersen <jpetersenames@gmail.com>
#

#!/usr/bin/python

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

# Open up SPI
spi = spidev.SpiDev()
spi.open(0,0)

# This function returns the converted
# ADC voltage from the 10-bit ADC
def adc_to_volt(reading):
    return float((reading * ADC_vcc) / 1024)

# This function returns the 10-bit integer
# received from the ADC.
def get_adc(channel):
    if ((channel > 7) or (channel < 0)):
        return ERROR
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3)<<8)+adc[2]
    return data

# This function returns the oversampled
# current value from the ACS712
def get_current():
    acs_offset = 2.438
    acs_step   = 0.185
    reading = get_adc(current_channel)
    adc_volt = adc_to_volt(reading)
    adj_volt = adc_volt - acs_offset
    current  = adj_volt / acs_step
    return current


try:
    # Get the time and create file name
    filename = "volt_current_sampling_rate.csv"

    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Voltage [V]', 'Current[A]'])

        while True:

            # Get the measurements
            time = str(datetime.datetime.now().time())
            volt = adc_to_volt(get_adc(voltage_channel))
            acs_current = get_current()

            # Write to csv
            csv_w.writerow([time, volt, acs_current])

# Close up the spi..
finally:
    spi.close()
