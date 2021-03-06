import os
import re
import datetime
import logging
import zope.interface
from thrush import rrd

from alerts import template_loader
from alerts.lib import Message
from alerts.lib.collected_stats import Stats as BaseStats
from alerts.lib.checkers import BaseChecker, named_checker

class Stats(BaseStats):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

@named_checker('nginx')
class Checker(BaseChecker):

    def __init__(self):
        BaseChecker.__init__(self)
        self.max_level = None
        self.start = None
        self._esolution = None
        return

    def setup(self, collection_dir, logger, opts):
        BaseChecker.setup(self, collection_dir, logger, opts)
        self.max_level = int(opts.get('usage_level', 1000)) # number of connections 
        self.start = '-%ds' % (int(opts.get('interval', 600)))
        self.resolution = '%d' % (int(opts.get('resolution', 120)))
        return
    
    def check(self, hostname):
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        max_u = self.max_level
        
        # Todo

        return
        
    def get_usage(self, data_dir):
        rrd_file = os.path.join(data_dir, 'nginx/nginx_connections-active.rrd')
        stats = Stats(rrd_file)
        return stats.avg('value', self.start, self.resolution)
    
