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

class Usage(namedtuple('Usage', ('used', 'reserved', 'free'))):
    
    def as_percentage(self):
        if self.used > 0:
            return 100.0 * (self.used + self.reserved)/(self.used + self.reserved + self.free)
        else:
            return .0
 
@named_checker('df')
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
        self.max_level = int(opts.get('usage_level', 90)) # 
        self.start = '-%ds' % (int(opts.get('interval', 1200)))
        self.resolution = '%d' % (int(opts.get('resolution', 600)))
        return
    
    def check(self, hostname):
        
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        max_u = self.max_level

        fs_names = self.find_fs_names(data_dir)
        
        # Check space
        
        for name in fs_names:
            try:
                uv = self.get_usage_of_space(data_dir, name)
            except NotEnoughData as ex:
                tpl = template_loader.load('not-enough-data.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    exc_message = str(ex),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Not enough data for filesystem usage at %s' % (hostname),
                    summary = u'Not enough data for filesystem <%s>: Skipping' % (name),
                    body = msg_body.render('html'))
                log1.warn(msg)
                continue # skip to next filesystem
            u = uv.as_percentage()
            if u > max_u:
                tpl = template_loader.load('df.excessive-usage.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    fs_name = name,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Running out of space at %s' %(hostname),
                    summary = u'Check df space at <%s>: FAILED (%.1f > %.1f)' %(name, u, max_u),
                    body = msg_body.render('html'))
                log1.warn(msg)
            else:
                msg = Message(
                    title = u'Checking df space at %s' % (hostname),
                    summary = u'Check df space at <%s>: OK (%.1f < %.1f)' % (name, u, max_u),
                    body = None)
                log1.info(msg)
            
        # Check inodes
        
        for name in fs_names:
            try:
                uv = self.get_usage_of_inodes(data_dir, name)
            except NotEnoughData as ex:
                tpl = template_loader.load('not-enough-data.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    exc_message = str(ex),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Not enough data for inodes usage at %s' % (hostname),
                    summary = u'Not enough data for inodes at <%s>: Skipping' % (name),
                    body = msg_body.render('html'))
                log1.warn(msg)
                continue # skip to next filesystem
            u = uv.as_percentage()
            if u > max_u:
                tpl = template_loader.load('df.excessive-usage-of-inodes.html')
                msg_body = tpl.generate(
                    hostname = hostname,
                    fs_name = name,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.datetime.now())
                msg = Message(
                    title = u'Running out of inodes at %s' %(hostname),
                    summary = u'Check df inodes at <%s>: FAILED (%.1f > %.1f)' %(name, u, max_u),
                    message = msg_body.render('html'))
                log1.warn(msg)
            else:
                msg = Message(
                    title = u'Checking df inodes at %s' % (hostname),
                    summary = u'Check df inodes at <%s>: OK (%.1f < %.1f)' % (name, u, max_u),
                    body = None)
                log1.info(msg)
        return
    
    ## Helpers ##

    def get_usage_of_space(self, data_dir, fs_name):
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_complex-free.rrd' % (fs_name))
        stats = Stats(rrd_file)
        free_bytes = stats.avg('value', self.start, self.resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_complex-reserved.rrd' % (fs_name))
        stats = Stats(rrd_file)
        reserved_bytes = stats.avg('value', self.start, self.resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_complex-used.rrd' % (fs_name))
        stats = Stats(rrd_file)
        used_bytes = stats.avg('value', self.start, self.resolution)
        
        return Usage(
            free = free_bytes,
            used = used_bytes,
            reserved = reserved_bytes) 

    def get_usage_of_inodes(self, data_dir, fs_name):
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_inodes-free.rrd' % (fs_name))
        stats = Stats(rrd_file)
        free_inodes = stats.avg('value', self.start, self.resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_inodes-reserved.rrd' % (fs_name))
        stats = Stats(rrd_file)
        reserved_inodes = stats.avg('value', self.start, self.resolution)
        
        rrd_file = os.path.join(data_dir, 'df-%s/df_inodes-used.rrd' % (fs_name))
        stats = Stats(rrd_file)
        used_inodes = stats.avg('value', self.start, self.resolution)
        
        return Usage(
            free = free_inodes,
            used = used_inodes,
            reserved = reserved_inodes) 
   
    @staticmethod
    def find_fs_names(data_dir):
        res = []
        for f in os.listdir(data_dir):
            m = re.match('^df-(.*)$', f)
            if m:
                res.append(m.group(1))
        return res

