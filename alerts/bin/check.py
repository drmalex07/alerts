#!/usr/bin/env python

import os
import sys
import argparse
import logging
import logging.config
from datetime import datetime, timedelta
from ConfigParser import ConfigParser
from paste.deploy.converters import asbool, asint, aslist

from alerts import config, config_from_file
from alerts.lib.checkers import checker_for

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
    
    config_from_file(args.config_file)
    
    # Setup notifiers (loggers)

    logging.config.fileConfig(args.config_file)
   
    # Perform checks
    
    log1 = logging.getLogger(__name__)
    hosts = args.hosts
    if not hosts and args.check_all:
        # List all hosts known to collectd daemon
        data_dir = config['stats']['collection_dir']
        hosts = os.listdir(data_dir)
        log1.info('Found hosts: %s', ', '.join(hosts))

    for name in aslist(config['alerts']['check']):
        c = checker_for(name)
        if c:
            for host in hosts:
                c.check(host)
        else:
            log1.info('Cannot find a `%s` checker', name)
