import time
import datetime

d1 = datetime.datetime.now()
for i in xrange(100):
#    tm = datetime.datetime.now()
#    print str(tm.microsecond)
    tm = datetime.datetime.now()
    tmd = (tm - d1).total_seconds()
    print tmd
    
