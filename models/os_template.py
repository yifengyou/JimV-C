#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import FilterFieldType
from models import ORM


__author__ = 'James Iter'
__date__ = '2017/3/23'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class OSTemplate(ORM):

    _table_name = 'os_template'
    _primary_key = 'id'

    def __init__(self):
        super(OSTemplate, self).__init__()
        self.id = 0
        self.label = None
        self.path = None
        self.active = None
        self.os_init_id = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'path': FilterFieldType.STR.value,
            'active': FilterFieldType.BOOL.value,
            'os_init_id': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['active', 'os_init_id']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'path']

