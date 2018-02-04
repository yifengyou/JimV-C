#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import FilterFieldType
from models import ORM


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class OSTemplateProfile(ORM):

    _table_name = 'os_template_profile'
    _primary_key = 'id'

    def __init__(self):
        super(OSTemplateProfile, self).__init__()
        self.id = 0
        self.label = None
        self.describe = ''
        self.os_type = None
        self.os_distro = None
        self.os_major = None
        self.os_minor = None
        self.os_arch = None
        self.os_product_name = None
        self.active = True
        self.icon = None
        self.os_template_initialize_operate_set_id = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'os_type': FilterFieldType.STR.value,
            'os_distro': FilterFieldType.STR.value,
            'os_product_name': FilterFieldType.STR.value,
            'os_template_initialize_operate_set_id': FilterFieldType.INT.value,
            'active': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['os_type', 'os_distro', 'os_arch', 'active', 'icon', 'os_template_initialize_operate_set_id']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'os_type', 'os_distro', 'os_product_name']

