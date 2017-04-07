#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import jimit as ji
import time

from models import Database as db
from models import FilterFieldType
from models import ORM
from models import Utils
from models.initialize import app, logger


__author__ = 'James Iter'
__date__ = '2017/4/8'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Log(ORM):

    _table_name = 'log'
    _primary_key = 'id'

    def __init__(self, **kwargs):
        super(Log, self).__init__()
        self.id = 0
        self.type = kwargs.get('type', None)
        self.timestamp = kwargs.get('timestamp', 0)
        self.host = kwargs.get('host', None)
        self.message = kwargs.get('message', None)

    def set(self, **kwargs):
        self.type = kwargs.get('type', None)
        self.timestamp = kwargs.get('timestamp', 0)
        self.host = kwargs.get('host', None)
        self.message = kwargs.get('message', None)

    @staticmethod
    def get_filter_keywords():
        return {
            'type': FilterFieldType.INT.value,
            'timestamp': FilterFieldType.INT.value,
            'host': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['host']

    @classmethod
    def launch(cls):

        log = Log()

        while True:
            if Utils.exit_flag:
                Utils.thread_counter -= 1
                print 'Thread say bye-bye'
                return

            try:
                host_log = db.r.lpop(app.config['host_event_report_queue'])

                if host_log is None:
                    time.sleep(1)
                    continue

                host_log = json.loads(host_log)
                log.set(type=host_log['type'], timestamp=host_log['timestamp'], host=host_log['host'],
                        message=host_log['message'])

                log.create()

            except Exception as e:
                logger.error(e.message)

