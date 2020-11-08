#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from filter import FilterFieldType
from orm import ORM


__author__ = 'James Iter'
__date__ = '2017/9/14'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class User(ORM):

    _table_name = 'user'
    _primary_key = 'id'

    def __init__(self, **kwargs):
        super(User, self).__init__()
        self.id = 0
        self.login_name = kwargs.get('login_name', None)
        self.password = kwargs.get('password', None)
        self.create_time = ji.Common.tus()
        self.mobile_phone = ''
        self.email = ''
        self.mobile_phone_verified = False
        self.email_verified = False
        self.enabled = True
        self.role_id = 0

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'login_name': FilterFieldType.STR.value,
            'create_time': FilterFieldType.INT.value,
            'mobile_phone': FilterFieldType.STR.value,
            'email': FilterFieldType.STR.value,
            'mobile_phone_verified': FilterFieldType.BOOL.value,
            'email_verified': FilterFieldType.BOOL.value,
            'enabled': FilterFieldType.BOOL.value,
            'role_id': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['mobile_phone_verified', 'email_verified', 'enabled', 'role_id']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['login_name', 'mobile_phone', 'email']

