#!/usr/bin/env python
# -*- coding: utf-8 -*-


from multiprocessing import JoinableQueue
from flask import Flask
from flask_socketio import SocketIO
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import os
import sys
import re
import getopt
import jimit as ji
import time
import errno

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
        'config_file': '/etc/jimvc.conf',
        'log_cycle': 'D',
        'instruction_channel': 'C:Instruction',
        'ip_available_set': 'S:IP:Available',
        'ip_used_set': 'S:IP:Used',
        'vnc_port_available_set': 'S:VNCPort:Available',
        'vnc_port_used_set': 'S:VNCPort:Used',
        'downstream_queue': 'Q:Downstream',
        'upstream_queue': 'Q:Upstream',
        'hosts_info': 'H:HostsInfo',
        'guest_boot_jobs': 'S:GuestBootJobs',
        'guest_boot_jobs_wait_time': 600,
        'db_charset': 'utf8',
        'db_pool_size': 10,
        'DEBUG': False,
        'jwt_algorithm': 'HS512',
        'token_ttl': 604800,
        'SESSION_TYPE': 'filesystem',
        'SESSION_PERMANENT': True,
        'SESSION_USE_SIGNER': True,
        'SESSION_FILE_DIR': '/tmp/jimv',
        'SESSION_FILE_THRESHOLD': 5000,
        'SESSION_COOKIE_NAME': 'sid',
        'SESSION_COOKIE_SECURE': False,
        'PERMANENT_SESSION_LIFETIME': 604800
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
            raise PathNotExist(u'配置文件不存在, 请指明配置文件路径')

        with open(cls.config['config_file'], 'r') as f:
            cls.config.update(json.load(f))

        return cls.config

    @classmethod
    def init_logger(cls):
        log_dir = os.path.dirname(cls.config['log_file_path'])
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir, 0755)
            except OSError as e:
                # 如果配置文件中的日志目录无写入权限，则调整日志路径到本项目目录下
                if e.errno != errno.EACCES:
                    raise

                cls.config['log_file_path'] = './logs/jimvc.log'
                log_dir = os.path.dirname(cls.config['log_file_path'])

                if not os.path.isdir(log_dir):
                    os.makedirs(log_dir, 0755)

                print u'日志路径自动调整为 ' + cls.config['log_file_path']

        _logger = logging.getLogger(cls.config['log_file_path'])

        if cls.config['DEBUG']:
            _logger.setLevel(logging.DEBUG)
        else:
            _logger.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(cls.config['log_file_path'], when=cls.config['log_cycle'],
                                      interval=1, backupCount=7)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s')
        fh.setFormatter(formatter)
        _logger.addHandler(fh)
        return _logger

    @staticmethod
    def pub_sub_ping_pong():
        from models import Database as db
        from models import Utils

        while True:
            if Utils.exit_flag:
                print 'Thread pub_sub_ping_pong say bye-bye'
                return

            time.sleep(10)
            db.r.publish(app.config['instruction_channel'], message=json.dumps({'action': 'ping'}))

    @staticmethod
    def clear_expire_monitor_log():
        from models import CPUMemory, Traffic, DiskIO, HostCPUMemory, HostTraffic, HostDiskUsageIO
        from models import Utils

        already_clear = False
        the_time = '03:30'

        while True:
            if Utils.exit_flag:
                print 'Thread clear_expire_monitor_log say bye-bye'
                return

            time.sleep(10)

            # 每天凌晨3点30分执行，清除15天前的监控记录
            if ji.JITime.now_time()[:5] == the_time and not already_clear:
                boundary = ji.Common.ts() - 86400 * 15
                filter_str = 'timestamp:lt:' + boundary.__str__()

                CPUMemory.delete_by_filter(filter_str=filter_str)
                Traffic.delete_by_filter(filter_str=filter_str)
                DiskIO.delete_by_filter(filter_str=filter_str)

                HostCPUMemory.delete_by_filter(filter_str=filter_str)
                HostTraffic.delete_by_filter(filter_str=filter_str)
                HostDiskUsageIO.delete_by_filter(filter_str=filter_str)

                already_clear = True

            if already_clear and ji.JITime.now_time()[:5] != the_time:
                already_clear = False


q_ws = JoinableQueue()
# 预编译效率更高
regex_sql_str = re.compile('\\\+"')
regex_dsl_str = re.compile('^\w+:\w+:[\S| ]+$')

config = Init.load_config()
logger = Init.init_logger()

app.config = dict(app.config, **config)
socketio = SocketIO(app)

ji.index_state['branch'] = dict(ji.index_state['branch'], **own_state_branch)

# sequence_device_node_mapping = ['vda', 'vdb', 'vdc', 'vdd']
dev_table = list()

for i in range(26):
    dev_table.append('vd' + chr(97 + i))

app.jinja_env.add_extension('jinja2.ext.loopcontrols')
