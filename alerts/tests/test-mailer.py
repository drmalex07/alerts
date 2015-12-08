#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from datetime import datetime
from paste.deploy.converters import asbool, asint, aslist

from alerts import config, template_loader, config_from_file
from alerts.lib.mailer import Mailer, make_mailer

if __name__ == '__main__':
    config_from_file('config.ini')

    m = make_mailer(config['mailer'])
    headers = {
        'Subject': 'Testing alerts.lib.mailer!',
    }

    t1 = template_loader.load('hello.html')
    values = {
        'title': u'Hello World',
        'message': u'Καλημέρα Κόσμε!! Τρα λαλα λαλα λαλα!',
        'generated_at': datetime.now(),
    }
    msg = t1.generate(**values).render('html')
    
    recipients = aslist(config['notifier']['recipients']),
    m.send(recipients[0], headers, msg)


