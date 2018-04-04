
import datetime
import spidev
import time
import csv

# pseudo defines
ERROR = -1

# Variables
ADC_vcc         = 5.0
voltage_channel = 0

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



try:
    # Get the time and create file name
    filename = "voltage_sampling_rate.csv"

    with open(filename, 'wb') as outfile:
        csv_w = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_w.writerow(['Time (h:m:s)', 'Voltage [V]'])

        while True:

            # Get the measurements
            volt = adc_to_volt(get_adc(voltage_channel))
            time        = str(datetime.datetime.now().time())
            # Write to csv
            csv_w.writerow([time, volt])

# Close up the spi..
finally:
    spi.close()
