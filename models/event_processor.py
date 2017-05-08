#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import time

from models import Database as db
from models import Guest
from models import GuestDisk
from models import Log
from models import Utils
from models import EmitKind
from models import ResponseState, GuestState, DiskState
from models.initialize import app, logger


__author__ = 'James Iter'
__date__ = '2017/4/15'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class EventProcessor(object):
    message = None
    log = Log()
    guest = Guest()
    disk = GuestDisk()

    @classmethod
    def log_processor(cls):
        cls.log.set(type=cls.message['type'], timestamp=cls.message['timestamp'], host=cls.message['host'],
                    message=cls.message['message'])

        cls.log.create()

    @classmethod
    def event_processor(cls):
        cls.guest.uuid = cls.message['message']['uuid']
        cls.guest.get_by('uuid')
        cls.guest.status = cls.message['type']
        cls.guest.on_host = cls.message['host']
        cls.guest.update()

    @classmethod
    def response_processor(cls):
        action = cls.message['message']['action']
        uuid = cls.message['message']['uuid']
        state = cls.message['type']

        if action == 'create_vm':
            if state != ResponseState.success.value:
                cls.guest.uuid = uuid
                cls.guest.get_by('uuid')
                cls.guest.status = GuestState.dirty.value
                cls.guest.update()

        elif action == 'create_disk':
            cls.disk.uuid = uuid
            cls.disk.get_by('uuid')
            if state == ResponseState.success.value:
                cls.disk.state = DiskState.idle.value

            else:
                cls.disk.state = DiskState.dirty.value

            cls.disk.update()

        else:
            pass

    @classmethod
    def launch(cls):
        while True:
            if Utils.exit_flag:
                Utils.thread_counter -= 1
                print 'Thread EventProcessor say bye-bye'
                return

            try:
                report = db.r.lpop(app.config['upstream_queue'])

                if report is None:
                    time.sleep(1)
                    continue

                cls.message = json.loads(report)

                if cls.message['kind'] == EmitKind.log.value:
                    cls.log_processor()

                elif cls.message['kind'] == EmitKind.event.value:
                    cls.event_processor()

                elif cls.message['kind'] == EmitKind.response.value:
                    cls.response_processor()

                else:
                    pass

            except Exception as e:
                logger.error(e.message)

