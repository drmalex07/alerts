#!/usr/bin/env python

import logging
import logging.config

from alerts import config, config_from_file
from alerts.lib import Message, CheckContext, ICheckContext
from alerts.lib.loggers import LoggingContext

if __name__ == '__main__':
    config_from_file('config.ini')
    logging.config.fileConfig('config.ini')

    log1 = logging.getLogger('checker.cpu')
    
    ctx = CheckContext(name='cpu', hostname='foo.localdomain')
    filt1 = LoggingContext(ctx)
    log1.addFilter(filt1)

    log1.info('Hello World (1)')
    
    msg = Message(summary='Hello World (2)', title='Greeting', body='I say hello to the whole world!')
    
    log1.info(msg)
    
    del log1
