import os
import logging
import zope.interface
import zope.schema
from zope.schema import getValidationErrors
from socket import getfqdn

from alerts import config
from .interfaces import ICheckContext
from .mailer import Mailer, make_mailer

## Filters ##

class LoggingContext(logging.Filter):
    
    def __init__(self, context):
        logging.Filter.__init__(self)
        
        errs = getValidationErrors(ICheckContext, context)
        if errs:
            raise ValueError('Not a proper context: %r' %(errs))
        self.context = context
    
    def filter(self, record):
        record.check_host = self.context.hostname
        record.checker_name = self.context.name
        return True

## Handlers ##

class MailHandler(logging.Handler):
    
    def __init__(self, recipients, mailer=None):
        logging.Handler.__init__(self)
        self.mailer = mailer or make_mailer(config['mailer'])
        self.recipients = recipients
    
    def emit(self, record):
        msg = record.msg
        try:
            # A structured message ?
            title, body = msg.title, msg.body
        except AttributeError:
            # A string-like message
            title = u'%s: Checking %s' % (record.levelname.lower(), record.check_host)
            body = record.getMessage()
        headers = {
            'Subject': unicode(title),
        }
        self.mailer.send(self.recipients, headers, body)
