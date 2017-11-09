#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import multiprocessing


__author__ = 'James Iter'
__date__ = '2017/2/20'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


with open('/etc/jimvc.conf', 'r') as f:
    _config = json.load(f)

log_file_dir = os.path.dirname(_config['log_file_path'])

if not os.path.isdir(log_file_dir):
    os.makedirs(log_file_dir, 0755)


bind = _config['listen'] + ':' + _config['port'].__str__()
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
daemon = True

accesslog = '/'.join([log_file_dir, 'access.log'])
errorlog = '/'.join([log_file_dir, 'error.log'])
loglevel = 'info'

pidfile = '/run/jimv/jimvc.pid'


