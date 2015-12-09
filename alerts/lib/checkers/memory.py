import os
import re
import datetime
import zope.interface
from thrush import rrd
from collections import namedtuple

from alerts import template_loader
from alerts.lib import Message
from alerts.lib.collected_stats import Stats as BaseStats
from alerts.lib.collected_stats import NoData, NotEnoughData
from alerts.lib.checkers import BaseChecker, named_checker

class Stats(BaseStats):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

class Usage(namedtuple('Usage', ('used', 'buffered', 'cached', 'free'))):
    
    def as_percentage(self):
        if self.used > 0:
            return 100.0 * (self.used)/(self.used + self.free + self.buffered + self.cached)
        else:
            return .0
    
@named_checker('memory')
class Checker(BaseChecker):
    
    def __init__(self):
        BaseChecker.__init__(self)
        self.max_level = None
        self.start = None
        self.resolution = None
        return

    ## IChecker interface ##
    
    def setup(self, collection_dir, logger, opts):
        
        BaseChecker.setup(self, collection_dir, logger, opts)
        self.max_level = int(opts.get('usage_level', 90)) # percentage
        self.start = '-%ds' % (int(opts.get('interval', 600)))
        self.resolution = '%d' % (int(opts.get('resolution', 120)))
        return
    
    def check(self, hostname):
        
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        try:
            uv = self.get_usage(data_dir)
        except NotEnoughData as ex:
            tpl = template_loader.load('not-enough-data.html')
            msg_body = tpl.generate(
                hostname = hostname,
                exc_message = str(ex),
                generated_at = datetime.datetime.now())
            msg = Message(
                title = u'Not enough data for memory usage at %s' % (hostname),
                summary = u'Not enough data for memory: Skipping',
                body = msg_body.render('html'))
            log1.warn(msg)
            return # skip checks

        max_u = self.max_level
        u = uv.as_percentage()
        log1.debug(
            'Computed memory usage: %.1f%% (%.1fMiB used, %.1fMiB free, %.1fMiB cached)', 
            u, (uv.used/(1<<20)), (uv.free/(1<<20)), (uv.cached/(1<<20)))
        if u > max_u:
            tpl = template_loader.load('memory.excessive-usage.html')
            msg_body = tpl.generate(
                hostname = hostname,
                max_usage = '%.1f' %(max_u),
                avg_usage = '%.1f' %(u),
                generated_at = datetime.datetime.now())
            msg = Message(
                title = u'Running out of memory at %s' %(hostname),
                summary = u'Check memory usage: FAILED (%.1f > %.1f)' %(u, max_u),
                body = msg_body.render('html'))
            log1.warn(msg)
        else:
            msg = Message(
                title = u'Checking memory at %s' % (hostname),
                summary = u'Check memory: OK (%.1f < %.1f)' % (u, max_u),
                body = None)
            log1.info(msg)
        return
        
    ## Helpers ##
    
    def get_usage(self, data_dir):
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-free.rrd'))
        free_bytes = stats.avg('value', self.start, self.resolution)
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-buffered.rrd'))
        buffered_bytes = stats.avg('value', self.start, self.resolution)
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-cached.rrd'))
        cached_bytes = stats.avg('value', self.start, self.resolution)
        
        stats = Stats(os.path.join(data_dir, 'memory/memory-used.rrd'))
        used_bytes = stats.avg('value', self.start, self.resolution)
        
        return Usage(
            free = free_bytes,
            used = used_bytes,
            cached = cached_bytes,
            buffered = buffered_bytes)
        
