import os
import re
import datetime
import zope.interface
from thrush import rrd

from alerts import template_loader
from alerts.lib import Message
from alerts.lib.collected_stats import Stats as BaseStats
from alerts.lib.collected_stats import NoData, NotEnoughData
from alerts.lib.checkers import BaseChecker, named_checker

class Stats(BaseStats):

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

@named_checker('cpu')
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
        self.max_level = int(opts.get('usage_level', 85)) # jiffies
        self.start = '-%ds' % (int(opts.get('interval', 1800)))
        self.resolution = '%d' % (int(opts.get('resolution', 60)))
        return
    
    def check(self, hostname):
        
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        max_u = self.max_level

        n = self.find_number_of_cpus(data_dir)
        for i in range(0, n):
            try:
                u = self.get_usage(data_dir, i, 'user')
            except NotEnoughData as ex:
                tpl = template_loader.load('not-enough-data.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    exc_message = str(ex),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Not enough data for processor usage at %s' % (hostname),
                    summary = u'Not enough data for CPU #%d: Skipping' % (i),
                    body = msg_body.render('html'))
                log1.warn(msg)
                continue # skip to next processor
            else:
                log1.debug('Computed usage for CPU #%d: %.2f', i, u)
            if u > max_u:
                tpl = template_loader.load('cpu.excessive-usage.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    cpu_number = i,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Processor overload at %s' %(hostname),
                    summary = u'Check CPU #%d: FAILED (%.1f > %.1f)' %(i, u, max_u),
                    body = msg_body.render('html'))
                log1.warn(msg)
            else:
                msg = Message(
                    title = u'Processor usage at %s' %(hostname),
                    summary = u'Check CPU #%d: OK (%.1f < %.1f)' % (i, u, max_u),
                    body = None)
                log1.info(msg)
        return
    
    ## Helpers ##

    def get_usage(self, data_dir, cpu_number, state='user'):
        rrd_file = os.path.join(data_dir, 'cpu-%d/cpu-%s.rrd' % (cpu_number, state))
        stats = Stats(rrd_file)
        return stats.avg('value', self.start, self.resolution)
    
    @staticmethod 
    def find_number_of_cpus(data_dir):
        max_i = -1
        for f in os.listdir(data_dir):
            m = re.match('^cpu-([0-9][0-9]?)$', f)
            if m:
                max_i = max(max_i, int(m.group(1)))
        return max_i + 1
