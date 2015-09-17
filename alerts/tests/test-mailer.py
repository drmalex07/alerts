#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from datetime import datetime

from alerts import config, template_loader, config_from_file
from alerts.lib.mailer import Mailer, make_mailer

if __name__ == '__main__':
    config_from_file('config.ini')

    m = make_mailer(config['mailer'])
    headers = {
        'Subject': 'Yet Another Test!',
    }

    t1 = template_loader.load('hello.html')
    values = {
        'title': u'Hello World',
        'message': u'Ακομη μια δοκιμαστικη παπαριά!',
        'generated_at': datetime.now(),
    }
    msg = t1.generate(**values).render('html')

    m.send('drmalex07@gmail.com', headers, msg)


