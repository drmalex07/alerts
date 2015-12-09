import os
import math
from datetime import datetime, timedelta
from thrush import rrd

# @Note: 
# The actual names of the following datasources (as well as their heartbeats) 
# can be found by running the appropriate `rrdtool info` commands

class NoData(RuntimeError): 
    
    pass

class NotEnoughData(RuntimeError): 
    
    pass

class Stats(object):
    
    # How many unknown CDPs can we tolerate and still consider
    # their aggregate (e.g AVERAGE) as meaningfull
    UNKNOWN_CDP_RATIO = 0.25

    # Represent data sources (DS) inside this RRD database
    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=300)

    def __init__(self, rrd_file):
        cls = type(self)
        self.db = cls.RRD(rrd_file)
        if not self.db.exists():
            raise Exception ('The RRD database %s does not exist!' %(rrd_file))
        return

    def avg(self, ds, start, resolution):
        '''Compute average in given window and resolution.
        '''
        
        res = None
        with self.db.fetch('AVERAGE', start=start, end='-0s', resolution=resolution) as res:
            ds_values = []
            n = 0
            for t, values in res:
                v = values[ds]
                n += 1
                if not (v is res.unknown) and (v == v):
                    ds_values.append(v)
            if n > 0:
                nv = len(ds_values)
                if float(nv) > (1 - self.UNKNOWN_CDP_RATIO) * (float(n - 1)):
                    res = math.fsum(ds_values) / nv
                else:
                    raise NotEnoughData(
                        '%s: Too many unknown CDPs (>%d%%) in window [%s, -0s]' % ( 
                            self.db.filename, int(100.0 * self.UNKNOWN_CDP_RATIO), start))
            else:
                raise NoData(
                    '%s: No CDPs found in window [%s, -0s]' % (
                        self.db.filename, start))
        return res
