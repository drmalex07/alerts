#!/usr/bin/env python

import thrush
import thrush.rrd

import random
import math
from datetime import datetime, timedelta

now = datetime.now()
step = timedelta(seconds=30)
t0 = now - timedelta(seconds=3600)

class FooData(thrush.rrd.RRD):
    value = thrush.rrd.Gauge(heartbeat=60)
    rra1 = thrush.rrd.Average(xff=0.5, steps=1, rows=128) # actual primary-data-point value
    rra2 = thrush.rrd.Average(xff=0.5, steps=12, rows=20) # average on 6min intervals
    rra3 = thrush.rrd.Average(xff=0.5, steps=60, rows=10) # average on 30min intervals

db = FooData("foo.rrd")
db.create(start=t0, step=30, overwrite=True)

# Feed RRD database with samples

v = .0
t = t0
for i in xrange(0,120):
    # feed samples in a step of 30s +/- 5s
    t = t + timedelta(seconds=(30 + random.randint(-5,5)))
    # calculate some value for datasource
    v = 10.0 * math.cos(0.25 * i)
    # update RRD database
    print 'Update at %s: v=%.1f' %(t.strftime("%T"), v)
    db.update(t, value=v)

# Print values from archive RRA3 (averages on 30min intervals)

with db.fetch(db.rra3.cf, start=t0, end=now, resolution=1800) as res:
    for timestamp, values in res:
        print '> %s %s' %(timestamp, values)

