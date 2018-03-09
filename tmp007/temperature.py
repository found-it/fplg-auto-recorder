from ctypes import *
from time import sleep

try:
    tm = CDLL('./tmp007.so')
    fd = tm.tmp007_setup()
    while(1):
        temp = float(tm.tmp007_read_temp(fd))
        print "[Python] Temp: ", str(temp), " F"
        print "----------------------------------\n"

except KeyboardInterrupt:
    print "Ended\n"

finally:
    print "Cleaning up..."
