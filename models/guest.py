#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from filter import FilterFieldType
from orm import ORM
from status import GuestState
from database import Database as db
from initialize import app


__author__ = 'James Iter'
__date__ = '2017/3/22'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Guest(ORM):

    _table_name = 'guest'
    _primary_key = 'id'

    def __init__(self):
        super(Guest, self).__init__()
        self.id = 0
        self.uuid = None
        self.name = None
        self.password = None
        self.remark = ''
        self.os_template_id = None
        self.create_time = ji.Common.tus()
        self.status = GuestState.no_state.value
        self.on_host = ''
        self.cpu = None
        self.memory = None
        self.ip = None
        self.network = None
        self.manage_network = None
        self.vnc_port = None
        self.vnc_password = None
        self.xml = None

    @staticmethod
    def get_filter_keywords():
        return {
            'name': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value,
            'on_host': FilterFieldType.STR.value,
            'ip': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['remark', 'cpu', 'memory', 'network', 'manage_network', 'vnc_password']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['name', 'remark', 'on_host', 'ip']

    @staticmethod
    def emit_instruction(message):
        db.r.publish(app.config['instruction_channel'], message=message)


class GuestDisk(ORM):

    _table_name = 'guest_disk'
    _primary_key = 'id'

    def __init__(self):
        super(GuestDisk, self).__init__()
        self.id = 0
        self.uuid = None
        self.label = None
        self.size = None
        self.sequence = None
        self.format = 'qcow2'
        self.guest_uuid = None

    @staticmethod
    def get_filter_keywords():
        return {
            'uuid': FilterFieldType.STR.value,
            'label': FilterFieldType.STR.value,
            'size': FilterFieldType.INT.value,
            'guest_uuid': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'size']



