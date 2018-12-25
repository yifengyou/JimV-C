#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from jimvc.models import FilterFieldType
from jimvc.models import ORM


__author__ = 'James Iter'
__date__ = '2018-12-25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class ReservedIP(ORM):

    _table_name = 'reserved_ip'
    _primary_key = 'id'

    def __init__(self):
        super(ReservedIP, self).__init__()
        self.id = 0
        self.ip = ''
        self.create_time = ji.Common.tus()

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'ip': FilterFieldType.STR.value,
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['ip']

