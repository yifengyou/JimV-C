#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from .filter import FilterFieldType
from .orm import ORM


__author__ = 'James Iter'
__date__ = '2018/10/7'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class Project(ORM):

    _table_name = 'project'
    _primary_key = 'id'

    def __init__(self):
        super(Project, self).__init__()
        self.id = 0
        self.name = ''
        self.description = ''
        self.create_time = ji.Common.tus()

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'name': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['name']


class Service(ORM):

    _table_name = 'service'
    _primary_key = 'id'

    def __init__(self):
        super(Service, self).__init__()
        self.id = 0
        self.project_id = 0
        self.name = ''
        self.description = ''
        self.create_time = ji.Common.tus()

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'project_id': FilterFieldType.INT.value,
            'name': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['project_id']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['name']
