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
        self.os_type = None
        self.active = None
        self.icon = None
        self.boot_job_id = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'path': FilterFieldType.STR.value,
            'os_type': FilterFieldType.INT.value,
            'active': FilterFieldType.BOOL.value,
            'boot_job_id': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['active', 'boot_job_id', 'os_type']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'path', 'os_type']

