#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import FilterFieldType
from models import ORM


__author__ = 'James Iter'
__date__ = '2017/3/23'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class OSInit(ORM):

    _table_name = 'os_init'
    _primary_key = 'id'

    def __init__(self):
        super(OSInit, self).__init__()
        self.id = 0
        self.name = None
        self.remark = ''

    @staticmethod
    def get_filter_keywords():
        return {
            'name': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['remark']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['name', 'remark']


class OSInitWrite(ORM):

    _table_name = 'os_init_write'
    _primary_key = 'id'

    def __init__(self):
        super(OSInitWrite, self).__init__()
        self.id = 0
        self.os_init_id = None
        self.path = ''
        self.content = ''

    @staticmethod
    def get_filter_keywords():
        return {
            'os_init_id': FilterFieldType.STR.value,
            'path': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['os_init_id', 'path']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['path', 'content']

