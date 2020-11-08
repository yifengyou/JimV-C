#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from filter import FilterFieldType
from orm import ORM


__author__ = 'James Iter'
__date__ = '2018/2/26'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class SSHKey(ORM):

    _table_name = 'ssh_key'
    _primary_key = 'id'

    def __init__(self):
        super(SSHKey, self).__init__()
        self.id = 0
        self.label = None
        self.public_key = None
        self.create_time = ji.Common.ts()

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'label': FilterFieldType.STR.value,
            'public_key': FilterFieldType.STR.value,
            'create_time': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label']

