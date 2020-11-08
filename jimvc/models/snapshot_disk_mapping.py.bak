#!/usr/bin/env python
# -*- coding: utf-8 -*-


from filter import FilterFieldType
from orm import ORM


__author__ = 'James Iter'
__date__ = '2018/4/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class SnapshotDiskMapping(ORM):

    _table_name = 'snapshot_disk_mapping'
    _primary_key = 'id'

    def __init__(self):
        super(SnapshotDiskMapping, self).__init__()
        self.id = 0
        self.snapshot_id = None
        self.disk_uuid = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'snapshot_id': FilterFieldType.STR.value,
            'disk_uuid': FilterFieldType.STR.value,
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['snapshot_id', 'disk_uuid']

