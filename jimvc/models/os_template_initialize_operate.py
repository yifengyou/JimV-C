#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jimvc.models import FilterFieldType
from jimvc.models import ORM


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class OSTemplateInitializeOperate(ORM):

    _table_name = 'os_template_initialize_operate'
    _primary_key = 'id'

    def __init__(self):
        super(OSTemplateInitializeOperate, self).__init__()
        self.id = 0
        self.os_template_initialize_operate_set_id = None
        self.kind = None
        self.sequence = None
        self.path = None
        self.content = None
        self.command = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'os_template_initialize_operate_set_id': FilterFieldType.INT.value,
            'sequence': FilterFieldType.INT.value,
            'command': FilterFieldType.STR.value,
            'path': FilterFieldType.STR.value,
            'content': FilterFieldType.STR.value,
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['os_template_initialize_operate_set_id']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['command', 'path', 'content']

