import os
import logging
import zope.interface
from zope.interface.verify import verifyObject

from alerts import config, template_loader
from alerts.lib.interfaces import adapter_registry
from alerts.lib.interfaces import INotifier, IChecker

def named_checker(name):
    def decorate(cls):
        adapter_registry.register([INotifier], IChecker, name, cls)
        return cls
    return decorate

def checker_for(name, notifier):
    verifyObject(INotifier, notifier) 
    checker = adapter_registry.queryAdapter(notifier, IChecker, name)
    if checker:
        data_dir = config['stats']['collectd_data_dir']
        pfx = name + '.'
        opts = {k[len(pfx):]: v 
            for k, v in config['alerts'].iteritems() if k.startswith(pfx)}
        checker.configure(data_dir, opts)
    return checker

# Provide context for loggers

class LoggingContext(logging.Filter):
    
    def __init__(self, host):
        super(LoggingContext, self).__init__()
        self.host = host
    
    def filter(self, record):
        record.check_host = self.host
        return True

# Import basic checkers

from . import cpu
from . import memory
from . import df
