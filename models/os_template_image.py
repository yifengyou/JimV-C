#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import FilterFieldType
from models import ORM


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class OSTemplateImage(ORM):

    _table_name = 'os_template_image'
    _primary_key = 'id'

    def __init__(self):
        super(OSTemplateImage, self).__init__()
        self.id = 0
        self.label = None
        self.description = None
        self.icon = None
        self.os_template_profile_id = None
        self.path = None
        self.active = True

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'path': FilterFieldType.STR.value,
            'os_template_profile_id': FilterFieldType.INT.value,
            'active': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'path']

