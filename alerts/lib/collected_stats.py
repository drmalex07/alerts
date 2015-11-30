import os
import math
from datetime import datetime, timedelta
from thrush import rrd

# @Note: 
# The actual names of the following datasources (as well as their heartbeats) 
# can be found by running the appropriate `rrdtool info` commands

class Stats(object):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=300)

    def __init__(self, rrd_file):
        cls = type(self)
        self.db = cls.RRD(rrd_file)
        if not self.db.exists():
            raise Exception ('The RRD database %s does not exist!' %(rrd_file))
        return

    def avg(self, ds, start, resolution):
        avg = None
        with self.db.fetch('AVERAGE', start=start, end='-0s', resolution=resolution) as res:
            ds_values = []
            for t, values in res:
                v = values[ds]
                if v == v:
                    ds_values.append(v)
            if ds_values:
                avg = math.fsum(ds_values)/len(ds_values)
            else:
                avg = .0
        return avg
