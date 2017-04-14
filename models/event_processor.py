#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import time

from models import Database as db
from models import Log
from models import Utils
from models import EmitKind
from models.initialize import app, logger


__author__ = 'James Iter'
__date__ = '2017/4/15'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class EventProcessor(object):
    message = None
    log = Log()

    @classmethod
    def log_processor(cls):
        cls.log.set(type=cls.message['type'], timestamp=cls.message['timestamp'], host=cls.message['host'],
                    message=cls.message['message'])

        cls.log.create()

    @classmethod
    def launch(cls):
        while True:
            if Utils.exit_flag:
                Utils.thread_counter -= 1
                print 'Thread EventProcessor say bye-bye'
                return

            try:
                host_log = db.r.lpop(app.config['host_event_report_queue'])

                if host_log is None:
                    time.sleep(1)
                    continue

                cls.message = json.loads(host_log)

                if cls.message['kind'] == EmitKind.log.value:
                    cls.log_processor()

                if cls.message['kind'] == EmitKind.event.value:
                    pass

            except Exception as e:
                logger.error(e.message)

