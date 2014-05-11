#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import genshi
from genshi.template import TemplateLoader
from ConfigParser import ConfigParser
from datetime import datetime

sys.path.append(os.path.realpath('.'))

import lib
from lib.mailer import Mailer, make_mailer

templates_dir1 = os.path.abspath('./templates');
template_loader = TemplateLoader([templates_dir1])

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')

    m = make_mailer(config)
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


