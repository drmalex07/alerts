#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import genshi
from genshi.template import TemplateLoader
from ConfigParser import ConfigParser
from datetime import datetime
from paste.deploy.converters import asbool, asint, aslist

sys.path.append(os.path.realpath('.'))

import lib
from lib.mailer import Mailer, make_mailer
from lib.notify import Message, MailNotifier

templates_dir1 = os.path.abspath('./templates');
template_loader = TemplateLoader([templates_dir1])

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')

    notifier = MailNotifier('Test-1',
        recipients = aslist(config.get('notify', 'recipients')),
        mailer = make_mailer(config)
    )

    tpl = template_loader.load('hello.html')

    values1 = {
        'title': u'Hello World',
        'message': u'Ακομη μια δοκιμαστικη παπαριά!',
        'generated_at': datetime.now(),
    }
    msg1 = Message(
        title = u'Another crap on the wall',
        summary = u'Something has happened',
        message = tpl.generate(**values1).render('html')
    )

    values2 = {
        'title': u'Goodbye World',
        'message': u'Εχετε γειά βρυσούλες!',
        'generated_at': datetime.now(),
    }
    msg2 = Message(
        title = u'Another goodbye',
        summary = u'Another goodbye',
        message = tpl.generate(**values2).render('html')
    )

    notifier.add_message(msg1, priority=0)
    notifier.add_message(msg2, priority=5)

    notifier.notify()

