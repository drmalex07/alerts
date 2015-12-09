import logging
import zope.interface

from alerts.lib.checkers import IChecker, BaseChecker

class Checker(BaseChecker):

    def __init__(self):
        BaseChecker.__init__(self)
        self.opts = None

    ## IChecker interface ##
    
    def setup(self, collection_dir, logger, opts):
        
        BaseChecker.setup(self, collection_dir, logger, opts)
        self.opts = opts.copy()
        return

    def check(self, hostname):
        
        log1 = self.get_logger(hostname)
        data_dir = self.data_dir(hostname)
        
        log1.info('Checking foo (data_dir is %s)', data_dir)
        return
