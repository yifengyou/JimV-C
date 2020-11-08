#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from .filter import FilterFieldType
from .orm import ORM


__author__ = 'James Iter'
__date__ = '2018/4/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class Snapshot(ORM):

    _table_name = 'snapshot'
    _primary_key = 'id'

    def __init__(self):
        super(Snapshot, self).__init__()
        self.id = 0
        self.label = None
        self.snapshot_id = None
        self.parent_id = None
        self.guest_uuid = None
        self.status = None
        self.progress = None
        self.create_time = ji.Common.tus()
        self.xml = ''

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'snapshot_id': FilterFieldType.STR.value,
            'guest_uuid': FilterFieldType.STR.value,
            'create_time': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'snapshot_id']

