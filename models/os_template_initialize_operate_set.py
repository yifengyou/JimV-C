#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import FilterFieldType
from models import ORM


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class OSTemplateInitializeOperateSet(ORM):

    _table_name = 'os_template_initialize_operate_set'
    _primary_key = 'id'

    def __init__(self):
        super(OSTemplateInitializeOperateSet, self).__init__()
        self.id = 0
        self.label = None
        self.description = ''
        self.active = True

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'active': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label']

