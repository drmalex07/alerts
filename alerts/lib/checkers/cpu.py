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
from alerts.lib.checkers import LoggingContext

class Stats(BaseStats):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

@named_checker('cpu')
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
        self._max_level = int(opts.get('usage_level', 85)) # jiffies
        self._start = '-%ds' % (int(opts.get('interval', 1800)))
        self._resolution = '%d' % (int(opts.get('resolution', 60)))
        return
    
    def check(self, hostname):
        log1 = logging.getLogger('checker.cpu')
        log1.addFilter(LoggingContext(hostname))

        data_dir = os.path.join(self._data_dir, hostname)
        
        max_u = self._max_level
        notifier = self._notifier

        n = self._find_number_of_cpus(data_dir)
        for i in range(0, n):
            u = self.get_usage(data_dir, i, 'user')
            log1.info('Computed usage for CPU #%d: %.2f', i, u)
            if u > max_u:
                tpl = template_loader.load('cpu.excessive-usage.html')
                msg = Message(
                    title = u'Processor overload at %s' %(hostname),
                    summary = u'CPU #%d exceeded usage limit of %d jiffies' %(i, max_u),
                    message = tpl.generate(
                        hostname = hostname,
                        cpu_number = i,
                        max_usage = '%.1f' %(max_u),
                        avg_usage = '%.1f' %(u),
                        generated_at = datetime.datetime.now()
                    ).render('html'),
                )
                notifier.add_message(msg, 0)
                log1.info('Check CPU #%d: FAILED (%.1f > %.1f)' %(i, u, max_u))
            else:
                log1.info('Check CPU #%d: OK (%.1f < %.1f)' %(i, u, max_u))
        return
        
    def get_usage(self, data_dir, cpu_number, state='user'):
        rrd_file = os.path.join(data_dir, 'cpu-%d/cpu-%s.rrd' % (cpu_number, state))
        stats = Stats(rrd_file)
        return stats.avg('value', self._start, self._resolution)
    
    @staticmethod 
    def _find_number_of_cpus(data_dir):
        max_i = -1
        for f in os.listdir(data_dir):
            m = re.match('^cpu-([0-9][0-9]?)$', f)
            if m:
                max_i = max(max_i, int(m.group(1)))
        return max_i + 1
