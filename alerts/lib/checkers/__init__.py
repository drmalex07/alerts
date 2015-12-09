import os
import hashlib
import logging
import zope.interface
import zope.schema
from zope.interface.verify import verifyObject
from zope.schema import getValidationErrors

from alerts import config, template_loader
from alerts.lib import CheckContext
from alerts.lib.loggers import LoggingContext
from alerts.lib.interfaces import adapter_registry
from alerts.lib.interfaces import IChecker

## Provide adapters ##

def named_checker(name):
    def decorate(cls):
        adapter_registry.register([], IChecker, name, cls)
        cls.__checker_name__ = name
        return cls
    return decorate

def checker_for(name):
    checker = adapter_registry.queryMultiAdapter([], IChecker, name)
    if not checker:
        return None
    
    # Collect relevant configuration options
    collection_dir = config['stats']['collection_dir']
    config_items = config['alerts'].iteritems()
    pfx = name + '.'
    opts = {key[len(pfx):]: val 
        for key, val in config_items if key.startswith(pfx)}
    
    # Setup this instance
    logger = logging.getLogger('checker.' + name)
    checker.setup(collection_dir, logger, opts)
    
    return checker

## Bases ##

@zope.interface.implementer(IChecker)
class BaseChecker(object):

    def __init__(self):
        self.collection_dir = None
        self.logger = None
        return
    
    def setup(self, collection_dir, logger, opts):
        self.collection_dir = collection_dir
        self.logger = logger
        return
    
    def get_logger(self, hostname):
        h = hashlib.md5(hostname).hexdigest()
        logger = self.logger.getChild(h)
        ctx = CheckContext(
            hostname=hostname, name=getattr(self, '__checker_name__', ''))
        logger.addFilter(LoggingContext(ctx))    
        return logger

    def data_dir(self, hostname):
        return os.path.join(self.collection_dir, hostname)
    
    def check(self, hostname):
        raise NotImplementedError('This is an abstract method')

## Import basic checkers ##

from . import cpu
from . import memory
from . import df
from . import curl
