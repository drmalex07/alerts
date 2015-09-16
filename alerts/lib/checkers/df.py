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

class Usage(namedtuple('Usage', ('used', 'reserved', 'free'))):
    
    def as_percentage(self):
        return 100.0 * (self.used + self.reserved)/(self.used + self.reserved + self.free)    
 
@named_checker('df')
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
        self._max_level = int(opts.get('usage_level', 90)) # 
        self._start = '-%ds' % (int(opts.get('interval', 1200)))
        self._resolution = '%d' % (int(opts.get('resolution', 600)))
        return
    
    def check(self, hostname):
        log1 = logging.getLogger('checker.df')
        log1.addFilter(LoggingContext(hostname))
        
        data_dir = os.path.join(self._data_dir, hostname)
        
        max_u = self._max_level
        notifier = self._notifier

        fs_names = self._find_fs_names(data_dir)
        for name in fs_names:
            # Check space
            uv = self.get_usage_of_space(data_dir, name)
            u = uv.as_percentage()
            log1.debug('Computed usage for filesystem `%s`: %.1f%% of space', name, u)
            if u > max_u:
                tpl = template_loader.load('df.excessive-usage.html')
                msg = Message(
                    title = u'Running out of space at %s' %(hostname),
                    summary = u'Used disk space exceeded %d%% at `%s`' %(max_u, name),
                    message = tpl.generate(
                        hostname = hostname,
                        fs_name = name,
                        max_usage = '%.1f' %(max_u),
                        avg_usage = '%.1f' %(u),
                        generated_at = datetime.datetime.now()
                    ).render('html')
                )
                notifier.add_message(msg, 0)
                log1.info('Check df space at `%s`: FAILED (%.1f > %.1f)' %(name, u, max_u))
            else:
                log1.info('Check df space at `%s`: OK (%.1f < %.1f)' %(name, u, max_u))
            
            # Check inodes
            uv = self.get_usage_of_inodes(data_dir, name)
            u = uv.as_percentage()
            log1.debug('Computed usage for filesystem `%s`: %.1f%% of inodes', name, u)
            if u > max_u:
                tpl = template_loader.load('df.excessive-usage-of-inodes.html')
                msg = Message(
                    title = u'Running out of inodes at %s' %(hostname),
                    summary = u'Used inodes exceeded %d%% at `%s`' %(max_u, name),
                    message = tpl.generate(
                        hostname = hostname,
                        fs_name = name,
                        max_usage = '%.1f' %(max_u),
                        avg_usage = '%.1f' %(u),
                        generated_at = datetime.datetime.now()
                    ).render('html')
                )
                notifier.add_message(msg, 0)
                log1.info('Check df inodes at `%s`: FAILED (%.1f > %.1f)' %(name, u, max_u))
            else:
                log1.info('Check df inodes at `%s`: OK (%.1f < %.1f)' %(name, u, max_u))

        return
        
    def get_usage_of_space(self, data_dir, fs_name):
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_complex-free.rrd' % (fs_name))
        stats = Stats(rrd_file)
        free_bytes = stats.avg('value', self._start, self._resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_complex-reserved.rrd' % (fs_name))
        stats = Stats(rrd_file)
        reserved_bytes = stats.avg('value', self._start, self._resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_complex-used.rrd' % (fs_name))
        stats = Stats(rrd_file)
        used_bytes = stats.avg('value', self._start, self._resolution)
        
        return Usage(
            free = free_bytes,
            used = used_bytes,
            reserved = reserved_bytes) 

    def get_usage_of_inodes(self, data_dir, fs_name):
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_inodes-free.rrd' % (fs_name))
        stats = Stats(rrd_file)
        free_inodes = stats.avg('value', self._start, self._resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_inodes-reserved.rrd' % (fs_name))
        stats = Stats(rrd_file)
        reserved_inodes = stats.avg('value', self._start, self._resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_inodes-used.rrd' % (fs_name))
        stats = Stats(rrd_file)
        used_inodes = stats.avg('value', self._start, self._resolution)
        
        return Usage(
            free = free_inodes,
            used = used_inodes,
            reserved = reserved_inodes) 
   
    @staticmethod
    def _find_fs_names(data_dir):
        res = []
        for f in os.listdir(data_dir):
            m = re.match('^df-(.*)$', f)
            if m:
                res.append(m.group(1))
        return res

