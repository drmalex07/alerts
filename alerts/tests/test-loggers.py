#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import logging
import logging.config
from datetime import datetime
from paste.deploy.converters import asbool, asint, aslist

from alerts import config_from_file, config, template_loader
from alerts.lib.mailer import Mailer, make_mailer
from alerts.lib import Message, CheckContext
from alerts.lib.loggers import LoggingContext

if __name__ == '__main__':
    config_from_file('config.ini')
    logging.config.fileConfig('config.ini')

    tpl = template_loader.load('hello.html')

    values1 = {
        'title': u'Hello World',
        'message': u'Ακομη μια δοκιμαστικη παπαριά!',
        'generated_at': datetime.now(),
    }
    msg1 = Message(
        title = u'Another crap on the wall',
        summary = u'Something has happened',
        body = tpl.generate(**values1).render('html')
    )
    
    print msg1.body

    log1 = logging.getLogger('checker.baz')
    ctx1 = CheckContext(name='baz', hostname='node1.localdomain')
    log1.addFilter(LoggingContext(ctx1))

    log1.warn(msg1)
