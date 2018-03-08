from time import sleep
import spidev

# Variables
acs_offset = 2.438
acs_step   = 0.185

# open up SPI
spi=spidev.SpiDev()
spi.open(0,0)


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


def get_current():
    reading = 0
    for i in xrange(127):
        reading = reading + get_adc(0)
    reading = reading>>7
    a2d_volt = adc_to_volt(reading)
    adj_volt = (a2d_volt - acs_offset)
    print adj_volt
    cur = adj_volt / acs_step
    print "Reading:     ", reading
    print "A2D Voltage: ", a2d_volt
    print "Current:     ", cur
    return cur

try:
    while True:
        sleep(0.5)
        acs_current = get_current()
        print "---------------------"

# close up the spi
finally:
    spi.close()
