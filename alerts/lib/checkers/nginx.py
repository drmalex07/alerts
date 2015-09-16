import os
import re
import datetime
import logging
import zope.interface
from thrush import rrd

from alerts import template_loader
from alerts.lib.notifiers import Message
from alerts.lib.collected_stats import Stats as BaseStats
from alerts.lib.checkers import IChecker, INotifier, named_checker

class Stats(BaseStats):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

@named_checker('nginx')
class Checker(object):
    
    zope.interface.implements(IChecker)

    def __init__(self, notifier):
        self._notifier = notifier
        self._data_dir = None
        self._max_level = None
        self._start = None
        self._resolution = None
        return

    def configure(self, data_dir, opts):
        self._data_dir = data_dir
        self._max_level = int(opts.get('usage_level', 1000)) # number of connections 
        self._start = '-%ds' % (int(opts.get('interval', 600)))
        self._resolution = '%d' % (int(opts.get('resolution', 120)))
        return
    
    def check(self, hostname):
        data_dir = os.path.join(self._data_dir, hostname)
        
        max_u = self._max_level
        notifier = self._notifier
        
        # Todo

        return
        
    def get_usage(self, data_dir):
        rrd_file = os.path.join(data_dir, 'nginx/nginx_connections-active.rrd')
        stats = Stats(rrd_file)
        return stats.avg('value', self._start, self._resolution)
    
