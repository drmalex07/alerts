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
    
    UNKNOWN_CDP_RATIO = 0.4 

    class RRD(rrd.RRD):
        value = rrd.Gauge(heartbeat=20)

@named_checker('curl')
class Checker(BaseChecker):

    def __init__(self):
        BaseChecker.__init__(self)
        self.max_response_time = None
        self.resolution = None
        self.start = None
        return
    
    ## IChecker interface ##

    def setup(self, collection_dir, logger, opts):
        
        BaseChecker.setup(self, collection_dir, logger, opts)
        self.max_response_time = 1e3 * float(opts.get('max_response_time', 8)) # milliseconds
        self.start = '-%ds' % (int(opts.get('interval', 300)))
        self.resolution = '%d' % (int(opts.get('resolution', 40)))
        return
    
    def check(self, hostname):
        
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        max_u = self.max_response_time
        
        for page_name in self.find_page_names(data_dir):
            try:
                u = 1e3 * self.get_response_time(data_dir, page_name)
            except NotEnoughData as ex:
                tpl = template_loader.load('curl.non-responsive-page.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    page_name = page_name,
                    exc_message = str(ex),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'The page "%s" is not responsive' % (page_name),
                    summary = u'The page "%s" is not responsive: Skipping' % (page_name),
                    body = msg_body.render('html'))
                log1.warn(msg)
                continue # skip to next page
            else:
                log1.debug('Computed response time for page "%s": %.1fms', page_name, u)
            
            if u > max_u:
                tpl = template_loader.load('curl.sluggish-page.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    page_name = page_name,
                    max_response_time = '%.1fms' % (max_u),
                    avg_response_time = '%.1fms' % (u),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'The page "%s" takes too long to respond' % (page_name),
                    summary = u'Check if page "%s" responsive: FAILED (%.1fms > %.1fms)' % (
                        page_name, u, max_u),
                    body = msg_body.render('html'))
                log1.warn(msg)
            else:
                msg = Message(
                    title = u'Check if page "%s" responsive' %(page_name),
                    summary = u'Check if page "%s" responsive: OK (%.1fms < %.1fms)' % (
                        page_name, u, max_u),
                    body = None)
                log1.info(msg)
                pass
            
        return
        
    ## Helpers ##

    def get_response_time(self, data_dir, page_name):
        rrd_file = os.path.join(data_dir, 'curl-%s/response_time.rrd' % (page_name))
        stats = Stats(rrd_file)
        return stats.avg('value', self.start, self.resolution)
    
    @staticmethod
    def find_page_names(data_dir):
        res = []
        for f in os.listdir(data_dir):
            m = re.match('^curl-(.*)$', f)
            if m:
                res.append(m.group(1))
        return res

