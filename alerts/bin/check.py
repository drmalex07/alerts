#!/usr/bin/env python

import os
import sys
import psutil
import genshi
import genshi.template
import logging
from datetime import datetime, timedelta
from ConfigParser import ConfigParser
from paste.deploy.converters import asbool, asint, aslist

sys.path.append(os.path.realpath('.'))

import lib
import lib.util as util
from lib.mailer import Mailer, make_mailer
from lib.notify import Message, Notifier, MailNotifier

templates_dir1 = os.path.abspath('./templates');
template_loader = genshi.template.TemplateLoader([templates_dir1])

if __name__ == '__main__':

    config = ConfigParser()
    config.read('config.ini')

    logging.basicConfig(level=logging.INFO)

    notifier_name = config.get('notify', 'notifier')
    notifier = None
    if notifier_name == 'mailer':
        notifier = MailNotifier(
            name = 'check',
            recipients = aslist(config.get('notify', 'recipients')),
            mailer = make_mailer(config)
        )
    else:
        notifier = Notifier('check')

    hostname = config.get('stats', 'hostname')
    collectd_data_dir = os.path.realpath(config.get('stats', 'collectd_data_dir'))

    util.COLLECTD_DATA_DIR = collectd_data_dir

    # 1. Check CPU usage

    max_u = float(config.get('alerts', 'cpu.usage_level'))
    for i in range(0, psutil.NUM_CPUS):
        u = util.get_cpu_usage(i)
        if u > max_u:
            tpl = template_loader.load('cpu.excessive-usage.html')
            msg = Message(
                title = u'Processor overload at %s' %(hostname),
                summary = u'CPU %d has exceeded the usage limit of %d jiffies' %(i, max_u),
                message = tpl.generate(
                    hostname = hostname,
                    cpu_number = i,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.now()
                ).render('html'),
            )
            notifier.add_message(msg, 0)
            logging.info('CPU #%d: FAILED (%.1f > %.1f)' %(i, u, max_u))
        else:
            logging.info('CPU #%d: OK (%.1f < %.1f)' %(i, u, max_u))

    # 2. Check memory usage

    max_u = float(config.get('alerts', 'memory.usage_level'))
    u = 100.0 * util.get_memory_usage()
    if u > max_u:
        tpl = template_loader.load('memory.excessive-usage.html')
        msg = Message(
            title = u'Running out of memory at %s' %(hostname),
            summary = u'Memory has exceeded the usage limit of %d%%' %(max_u),
            message = tpl.generate(
                hostname = hostname,
                max_usage = '%.1f' %(max_u),
                avg_usage = '%.1f' %(u),
                generated_at = datetime.now()
            ).render('html'),
        )
        notifier.add_message(msg, -5)
        logging.info('Memory: FAILED (%.1f > %.1f)' %(u, max_u))
    else:
        logging.info('Memory: OK (%.1f < %.1f)' %(u, max_u))

    # 3. Check filesystem usage

    max_u = float(config.get('alerts', 'fs.usage_level'))
    for partition in psutil.disk_partitions():
        mountpoint = partition.mountpoint
        # Check space
        u = 100.0 * util.get_fs_usage(mountpoint)
        if u > max_u:
            tpl = template_loader.load('fs.excessive-usage.html')
            msg = Message(
                title = u'Running out of space at %s' %(hostname),
                summary = u'Used disk space has exceeded %d%% at %s' %(max_u, mountpoint),
                message = tpl.generate(
                    hostname = hostname,
                    mountpoint = mountpoint,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.now()
                ).render('html')
            )
            notifier.add_message(msg, -5)
            logging.info('Disk(space):%s: FAILED (%.1f > %.1f)' %(mountpoint, u, max_u))
        else:
            logging.info('Disk(space):%s: OK (%.1f < %.1f)' %(mountpoint, u, max_u))
        # Check inodes
        u = 100.0 * util.get_fs_usage_of_inodes(mountpoint)
        if u > max_u:
            tpl = template_loader.load('fs.excessive-usage-of-inodes.html')
            msg = Message(
                title = u'Running out of inodes at %s' %(hostname),
                summary = u'Used inodes have exceeded %d%% at %s' %(max_u, mountpoint),
                message = tpl.generate(
                    hostname = hostname,
                    mountpoint = mountpoint,
                    max_usage = '%.1f' %(max_u),
                    avg_usage = '%.1f' %(u),
                    generated_at = datetime.now()
                ).render('html')
            )
            notifier.add_message(msg, -5)
            logging.info('Disk(inodes):%s: FAILED (%.1f > %.1f)' %(mountpoint, u, max_u))
        else:
            logging.info('Disk(inodes):%s: OK (%.1f < %.1f)' %(mountpoint, u, max_u))

    # 4. Check Nginx workload (active connections)

    # Todo

    # Send notifications (if any)

    notifier.notify()

