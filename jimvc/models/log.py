#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jimvc.models import FilterFieldType
from jimvc.models import ORM


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
        self.full_message = kwargs.get('full_message', None)

    def set(self, **kwargs):
        self.type = kwargs.get('type', None)
        self.timestamp = kwargs.get('timestamp', 0)
        self.host = kwargs.get('host', None)
        self.message = kwargs.get('message', None)
        self.full_message = kwargs.get('full_message', None)

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'type': FilterFieldType.INT.value,
            'timestamp': FilterFieldType.INT.value,
            'host': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['host', 'message']

