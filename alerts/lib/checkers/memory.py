import os
import re
import datetime
import logging
import zope.interface
from thrush import rrd
from collections import namedtuple

from alerts import template_loader
from alerts.lib.notifiers import Message
from alerts.lib.collected_stats import Stats as BaseStats
from alerts.lib.checkers import IChecker, INotifier, named_checker
from alerts.lib.checkers import LoggingContext

class Stats(BaseStats):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

class Usage(namedtuple('Usage', ('used', 'buffered', 'cached', 'free'))):
    
    def as_percentage(self):
        return 100.0 * (self.used)/(self.used + self.free + self.buffered + self.cached)    
    
@named_checker('memory')
class Checker(object):
    
    zope.interface.implements(IChecker)
    
    def __init__(self, notifier):
        self._log = logging.getLogger(__name__)
        self._notifier = notifier
        self._data_dir = None
        self._max_level = None
        self._start = None
        self._resolution = None
        return

    def configure(self, data_dir, opts):
        self._data_dir = data_dir
        self._max_level = int(opts.get('usage_level', 90)) # percentage
        self._start = '-%ds' % (int(opts.get('interval', 600)))
        self._resolution = '%d' % (int(opts.get('resolution', 120)))
        return
    
    def check(self, hostname):
        log1 = logging.getLogger('checker.memory')
        log1.addFilter(LoggingContext(hostname))
        
        data_dir = os.path.join(self._data_dir, hostname)
        
        max_u = self._max_level
        notifier = self._notifier

        uv = self.get_usage(data_dir)
        u = uv.as_percentage()
        log1.info(
            'Computed memory usage: %.1f%% (%.1fMiB used, %.1fMiB free, %.1fMiB cached)', 
            u, (uv.used/(1<<20)), (uv.free/(1<<20)), (uv.cached/(1<<20)))
        if u > max_u:
            tpl = template_loader.load('memory.excessive-usage.html')
            msg = Message(
                title = u'Running out of memory at %s' %(hostname),
                summary = u'Memory exceeded usage limit of %d%%' %(max_u),
                message = tpl.generate(
                    hostname = hostname,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.datetime.now()
                ).render('html'),
            )
            notifier.add_message(msg, -5)
            log1.info('Check memory: FAILED (%.1f > %.1f)' %(u, max_u))
        else:
            log1.info('Check memory: OK (%.1f < %.1f)' %(u, max_u))
        
        return
        
    def get_usage(self, data_dir):
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-free.rrd'))
        free_bytes = stats.avg('value', self._start, self._resolution)
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-buffered.rrd'))
        buffered_bytes = stats.avg('value', self._start, self._resolution)
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-cached.rrd'))
        cached_bytes = stats.avg('value', self._start, self._resolution)
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-used.rrd'))
        used_bytes = stats.avg('value', self._start, self._resolution)
        
        return Usage(
            free = free_bytes,
            used = used_bytes,
            cached = cached_bytes,
            buffered = buffered_bytes)
        
