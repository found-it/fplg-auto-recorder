

import time
import datetime

t1 = datetime.datetime.now()
while True:
    t2 = t1
    t1 = datetime.datetime.now()
    dt = t1 - t2
    sec = dt.total_seconds()
    print "Time diff: " + str(sec)


