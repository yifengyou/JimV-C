#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from jimvc.models import FilterFieldType
from jimvc.models import ORM


__author__ = 'James Iter'
__date__ = '2019-03-11'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2019 by James Iter.'


class VLAN(ORM):

    _table_name = 'vlan'
    _primary_key = 'id'

    def __init__(self):
        super(VLAN, self).__init__()
        self.id = 0
        self.vlan_id = None
        self.label = ''
        self.description = ''
        self.create_time = ji.Common.tus()

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.INT.value,
            'vlan_id': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['vlan_id', 'label', 'description']


