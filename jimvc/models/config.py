#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jimvc.models import app_config
from jimvc.models import Database as db
from jimvc.models import ORM
from jimvc.models import status


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Config(ORM):

    _table_name = 'config'
    _primary_key = 'id'

    def __init__(self):
        super(Config, self).__init__()
        # 配置条目的 id 只会是 1
        self.id = 1
        self.jimv_edition = status.JimVEdition.standalone.value
        self.storage_mode = status.StorageMode.local.value
        self.dfs_volume = ''
        self.storage_path = ''
        self.vm_network = ''
        self.vm_manage_network = ''
        self.iops_base = 0
        self.iops_pre_unit = 0
        self.iops_cap = 0
        self.iops_max = 0
        self.iops_max_length = 0
        self.bps_base = 0
        self.bps_pre_unit = 0
        self.bps_cap = 0
        self.bps_max = 0
        self.bps_max_length = 0

    @staticmethod
    def get_filter_keywords():
        return {}

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []

    def update_global_config(self):
        db.r.hmset(app_config['global_config'], self.__dict__)

