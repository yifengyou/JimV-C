#!/usr/bin/env python
# -*- coding: utf-8 -*-


from filter import FilterFieldType
from orm import ORM


__author__ = 'James Iter'
__date__ = '2018/3/1'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class SSHKeyGuestMapping(ORM):

    _table_name = 'ssh_key_guest_mapping'
    _primary_key = 'id'

    def __init__(self):
        super(SSHKeyGuestMapping, self).__init__()
        self.id = 0
        self.ssh_key_id = None
        self.guest_uuid = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'ssh_key_id': FilterFieldType.INT.value,
            'guest_uuid': FilterFieldType.STR.value,
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['guest_uuid']

