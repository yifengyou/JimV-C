#!/usr/bin/env python
# -*- coding: utf-8 -*-


from multiprocessing import JoinableQueue
from flask import Flask, g
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import os
import sys
import re
import getopt
import jimit as ji

from jimvc_exception import PathNotExist
from state_code import own_state_branch


reload(sys)
sys.setdefaultencoding('utf8')


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


app = Flask(__name__, template_folder='../templates', static_folder='../static')


class Init(object):
    config = {
        'config_file': '/etc/jimvc.conf'
    }

    @classmethod
    def load_config(cls):

        def usage():
            print "Usage:%s [-c] [--config]" % sys.argv[0]

        opts = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hc:',
                                       ['help', 'config='])
        except getopt.GetoptError as e:
            print str(e)
            usage()
            exit(e.message.__len__())

        for k, v in opts:
            if k in ("-h", "--help"):
                usage()
                exit()
            elif k in ("-c", "--config"):
                cls.config['config_file'] = v
            else:
                print "unhandled option"

        if not os.path.isfile(cls.config['config_file']):
            raise PathNotExist(u'配置文件不存在, 请配置 --> ', cls.config['config_file'])

        with open(cls.config['config_file'], 'r') as f:
            cls.config.update(json.load(f))

        return cls.config

    @classmethod
    def init_logger(cls):
        cls.config['log_file_base'] = '/'.join([sys.path[0], cls.config['log_file_dir'], 'log'])
        log_dir = os.path.dirname(cls.config['log_file_base'])
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir, 0755)

        process_title = 'JimV-C'
        log_file_path = '.'.join([cls.config['log_file_base'], process_title])
        _logger = logging.getLogger(log_file_path)

        if cls.config['debug']:
            cls.config['DEBUG'] = True
            _logger.setLevel(logging.DEBUG)
        else:
            cls.config['DEBUG'] = False
            _logger.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(log_file_path, when=cls.config['log_cycle'], interval=1, backupCount=7)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s')
        fh.setFormatter(formatter)
        _logger.addHandler(fh)
        return _logger


q_ws = JoinableQueue()
# 预编译效率更高
regex_sql_str = re.compile('\\\+"')
regex_dsl_str = re.compile('^\w+:\w+:[\S| ]+$')

config = Init.load_config()
logger = Init.init_logger()

app.config = dict(app.config, **config)

ji.index_state['branch'] = dict(ji.index_state['branch'], **own_state_branch)

# sequence_device_node_mapping = ['vda', 'vdb', 'vdc', 'vdd']
dev_table = ['vda', 'vdb', 'vdc', 'vdd']
