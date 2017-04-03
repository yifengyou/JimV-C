#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import multiprocessing


__author__ = 'James Iter'
__date__ = '2017/2/20'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


with open('./config.json', 'r') as f:
    _config = json.load(f)

if not os.path.isdir(_config['log_file_dir']):
    os.makedirs(_config['log_file_dir'], 0755)


bind = _config['jimid_listen'] + ':' + _config['jimid_port'].__str__()
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'eventlet'
worker_connections = 1000
daemon = True

accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'info'

pidfile = './jimid.pid'
