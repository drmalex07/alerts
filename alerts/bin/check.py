#!/usr/bin/env python

import os
import sys
import argparse
import logging
import logging.config
from datetime import datetime, timedelta
from ConfigParser import ConfigParser
from paste.deploy.converters import asbool, asint, aslist

from alerts import config, template_loader, config_from_file
from alerts.lib.interfaces import IChecker, INotifier
from alerts.lib.checkers import checker_for
from alerts.lib.notifiers import Message, Notifier, MailNotifier 
from alerts.lib.mailer import Mailer, make_mailer

if __name__ == '__main__':
    
    argp = argparse.ArgumentParser()
    argp.add_argument(
        'hosts', metavar='HOSTNAME', type=str, nargs='*')
    argp.add_argument(
        "-c", "--config", dest='config_file', default='config.ini', type=str)
    argp.add_argument(
        "-a", "--all", dest='check_all', default=False, action='store_true',
        help='Check all known hosts');
    
    args = argp.parse_args()
    
    logging.config.fileConfig(args.config_file)
    log1 = logging.getLogger(__name__)

    config_from_file(args.config_file)
   
    # Setup notifier
    
    notifier = None
    notifier_name = config['notifier']['notifier']
    if notifier_name == 'mailer':
        notifier = MailNotifier(
            name = 'check',
            recipients = aslist(config['notifier']['recipients']),
            mailer = make_mailer(config['mailer'])
        )
    else:
        notifier = Notifier('check')
   
    # Perform checks
    
    hosts = args.hosts
    if not hosts and args.check_all:
        # List all hosts known to collectd daemon
        data_dir = config['stats']['collectd_data_dir']
        hosts = os.listdir(data_dir)
        log1.info('Found hosts: %s', ', '.join(hosts))

    for name in aslist(config['alerts']['check']):
        c = checker_for(name, notifier)
        if c:
            for h in hosts:
                c.check(h)
        else:
            log1.info('Cannot find a `%s` checker', name)

    # Send notifications (if any)
    
    notifier.notify()
