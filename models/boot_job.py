#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import FilterFieldType
from models import ORM


__author__ = 'James Iter'
__date__ = '2017/6/19'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class BootJob(ORM):

    _table_name = 'boot_job'
    _primary_key = 'id'

    def __init__(self):
        super(BootJob, self).__init__()
        self.id = 0
        self.name = None
        self.use_for = None
        self.remark = ''

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'name': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['use_for']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['name', 'remark']


class OperateRule(ORM):

    _table_name = 'operate_rule'
    _primary_key = 'id'

    def __init__(self):
        super(OperateRule, self).__init__()
        self.id = 0
        self.boot_job_id = None
        self.kind = ''
        self.sequence = 0
        self.command = ''
        self.path = ''
        self.content = ''

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'boot_job_id': FilterFieldType.INT.value,
            'sequence': FilterFieldType.INT.value,
            'command': FilterFieldType.STR.value,
            'path': FilterFieldType.STR.value,
            'content': FilterFieldType.STR.value,
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['boot_job_id', 'sequence']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['command', 'path', 'content']


