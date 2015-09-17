#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
from datetime import datetime
from paste.deploy.converters import asbool, asint, aslist

from alerts import config_from_file, config, template_loader
from alerts.lib.mailer import Mailer, make_mailer
from alerts.lib.notifiers import Message, MailNotifier

if __name__ == '__main__':
    config_from_file('config.ini')

    notifier = MailNotifier('Test-1',
        recipients = aslist(config['notifier']['recipients']),
        mailer = make_mailer(config['mailer'])
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

