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

class Usage(namedtuple('Usage', ('running_threads', 'connected_threads'))):
    
    pass

@named_checker('mysql')
class Checker(BaseChecker):

    def __init__(self):
        BaseChecker.__init__(self)
        self.max_running_threads = None
        self.start = None
        self.resolution = None
        return

    ## IChecker interface ##

    def setup(self, collection_dir, logger, opts):
        
        BaseChecker.setup(self, collection_dir, logger, opts)
        self.max_running_threads = int(opts.get('max_running_threads', 180))
        self.start = '-%ds' % (int(opts.get('interval', 1800)))
        self.resolution = '%d' % (int(opts.get('resolution', 60)))
        return
    
    def check(self, hostname):
        
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        for db in self.find_databases(data_dir):
            try:
                u = self.get_usage(data_dir, db)
            except NotEnoughData as ex:
                tpl = template_loader.load('not-enough-data.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    exc_message = str(ex),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Not enough data for mysql (%s) at %s' % (hostname, db),
                    summary = u'Not enough data for mysql (%s): Skipping' % (db),
                    body = msg_body.render('html'))
                log1.warn(msg)
                continue # skip to next
            else:
                log1.debug(
                    'Computed usage for mysql (%s): %.1f connected, %.1f running',
                    db, u.connected_threads, u.running_threads)
            
            # Check number of running threads

            if u.running_threads > self.max_running_threads:
                tpl = template_loader.load('mysql.many-running-threads.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    database = db,
                    max_usage = '%d' %(self.max_running_threads),
                    avg_usage = '%.1f' %(u.running_threads),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'MySQL overload at %s' %(hostname),
                    summary = u'Check mysql (%s): FAILED (%.1f > %d running threads)' %(
                        db, u.running_threads, self.max_running_threads),
                    body = msg_body.render('html'))
                log1.warn(msg)
            else:
                msg = Message(
                    title = u'MySQL usage at %s' %(hostname),
                    summary = u'Check mysql (%s): OK (%.1f < %d running threads)' % (
                        db, u.running_threads, self.max_running_threads),
                    body = None)
                log1.info(msg)

        return
    
    ## Helpers ##

    def get_usage(self, data_dir, db):
        rrd_file = os.path.join(data_dir, 'mysql-%s/threads-running.rrd' % (db))
        stats = Stats(rrd_file)
        num_running_threads = stats.avg('value', self.start, self.resolution)
        
        rrd_file = os.path.join(data_dir, 'mysql-%s/threads-connected.rrd' % (db))
        stats = Stats(rrd_file)
        num_connected_threads = stats.avg('value', self.start, self.resolution)
    
        return Usage(
            running_threads = num_running_threads,
            connected_threads = num_connected_threads)

    @staticmethod 
    def find_databases(data_dir):
        res = []
        for f in os.listdir(data_dir):
            m = re.match('^mysql-([a-z][-_a-z0-9]*)$', f)
            if m:
                res.append(m.group(1))
        return res
