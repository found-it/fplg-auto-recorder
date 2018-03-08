from time import sleep
import spidev
spi=spidev.SpiDev()
spi.open(0,0)


def get_adc(channel):
        if ((channel > 1) or (channel < 0)):
                return -1

        r = spi.xfer2([1,(2+channel)<<6,0])
        ret = ((r[1]&31) << 6) + (r[2] >> 2)
        return ret


try:
    reading = 0
    while 1:
        for i in xrange(127):
            reading = reading + get_adc(0)
        reading = reading>>7
        print "Reading: ", reading
        a2d_volt = float((reading*3.3)/1024)
        print "A2D Voltage: ", a2d_volt
        adj_volt = (a2d_volt - 2.438)
        print adj_volt
        cur = adj_volt / 0.185
        print cur
        sleep(0.5)
        print "---------------------"

# close up the spi
finally:
    spi.close()
