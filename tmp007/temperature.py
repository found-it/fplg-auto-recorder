from ctypes import *
from time import sleep

try:
    tm = CDLL('./tmp007.so')
    fd = tm.tmp007_setup()
    while(1):
        tmp007_read_temp = tm.tmp007_read_temp
        tmp007_read_temp.restype = c_float
        temp = tmp007_read_temp(fd)
        print "[Python] Temp: ", str(temp), " F"
        print "----------------------------------\n"
        sleep(0.5)

except KeyboardInterrupt:
    print "Ended\n"

finally:
    print "Cleaning up..."
