#!/usr/bin/env python

import os
import sys
import psutil
from datetime import datetime, timedelta
from ConfigParser import ConfigParser
from paste.deploy.converters import asbool, asint, aslist

sys.path.append(os.path.realpath('.'))

import lib
from lib.util import get_cpu_usage, \
  get_memory_usage, get_memory_free_kilobytes, \
  get_fs_usage, get_fs_free_kilobytes

templates_dir1 = os.path.abspath('./templates');
template_loader = genshi.template.TemplateLoader([templates_dir1])

if __name__ == '__main__':

    config = ConfigParser()
    config.read('config.ini')

    for i in range(0, psutil.NUM_CPUS):
        print 'processor #%d: %.2f' %(i, get_cpu_usage(i))

    print 'memory (used): %.1f %%' %(100.0 * get_memory_usage())
    print 'memory (free): %d KiB' %(get_memory_free_kilobytes())

    for partition in psutil.disk_partitions():
        mountpoint = partition.mountpoint
        print 'filesystem: %.1f %% on %s (%d KiB free)' %(
            100.0 * get_fs_usage(mountpoint),
            mountpoint,
            get_fs_free_kilobytes(mountpoint)
        )

