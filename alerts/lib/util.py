import os
import psutil
from collections import namedtuple

import lib
import lib.collected_stats as collected_stats

COLLECTD_DATA_DIR='rrd-data'

def get_cpu_usage(cpu_number=None, start='-1800s', resolution='30'):
    if isinstance(cpu_number, int):
        rrd_file = os.path.join(COLLECTD_DATA_DIR, 'cpu-%d/cpu-user.rrd' % (cpu_number))
        cpu_stats = collected_stats.CpuStats(rrd_file)
        r = cpu_stats.avg('value', start, resolution)
        return r
    elif cpu_number is None:
        n = psutil.NUM_CPUS
        r = reduce(lambda s,i: s + get_cpu_usage(i, start, resolution), range(0, n), .0)
        return r / n
    else:
        raise ValueError('Expected an integer to describe the CPU number')

def get_memory_usage(start='-600s', resolution='120'):
    mem_info = psutil.virtual_memory()
    rrd_file = os.path.join(COLLECTD_DATA_DIR, 'memory/memory-free.rrd')
    mem_stats = collected_stats.MemoryStats(rrd_file)
    free_bytes = mem_stats.avg('value', start, resolution)
    total_bytes = mem_info.total
    return (1 - (free_bytes/total_bytes));

def get_memory_free_kilobytes(start='-600s', resolution='120'):
    rrd_file = os.path.join(COLLECTD_DATA_DIR, 'memory/memory-free.rrd')
    mem_stats = collected_stats.MemoryStats(rrd_file)
    free_bytes = mem_stats.avg('value', start, resolution)
    return (free_bytes / 1024);

def get_fs_usage(mountpoint, start='-1200s', resolution='600'):
    info = os.statvfs(mountpoint)
    name = mountpoint.strip('/')
    name = 'root' if (not len(name)) else name.replace('/','-')
    rrd_file = os.path.join(COLLECTD_DATA_DIR, 'df-%s/df_complex-free.rrd' %(name))
    disk_stats = collected_stats.DfStats(rrd_file)
    free_bytes = disk_stats.avg('value', start, resolution)
    total_bytes = info.f_blocks * info.f_bsize
    return (1 - (free_bytes/total_bytes))

def get_fs_usage_of_inodes(mountpoint, start='-1200s', resolution='600'):
    info = os.statvfs(mountpoint)
    name = mountpoint.strip('/')
    name = 'root' if (not len(name)) else name.replace('/','-')
    rrd_file = os.path.join(COLLECTD_DATA_DIR, 'df-%s/df_inodes-free.rrd' %(name))
    disk_stats = collected_stats.DfStats(rrd_file)
    free_inodes = disk_stats.avg('value', start, resolution)
    max_inodes = info.f_files
    return (1 - (free_inodes/max_inodes))

def get_fs_free_kilobytes(mountpoint, start='-1200s', resolution='600'):
    name = mountpoint.strip('/')
    name = 'root' if (not len(name)) else name.replace('/','-')
    rrd_file = os.path.join(COLLECTD_DATA_DIR, 'df-%s/df_complex-free.rrd' %(name))
    disk_stats = collected_stats.DfStats(rrd_file)
    free_bytes = disk_stats.avg('value', start, resolution)
    return (free_bytes / 1024)

def get_nginx_connections(start='-600s', resolution='60'):
    rrd_file = os.path.join(COLLECTD_DATA_DIR, 'nginx/nginx_connections-active.rrd')
    nginx_stats = collected_stats.NginxStats(rrd_file)
    r = nginx_stats.avg('value', start, resolution)
    return r

