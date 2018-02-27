#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji

from filter import FilterFieldType
from orm import ORM
from status import GuestState, DiskState


__author__ = 'James Iter'
__date__ = '2017/3/22'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Guest(ORM):

    _table_name = 'guest'
    _primary_key = 'id'

    def __init__(self):
        super(Guest, self).__init__()
        self.id = 0
        self.uuid = None
        self.label = None
        self.password = None
        self.remark = ''
        self.os_template_image_id = None
        self.create_time = ji.Common.tus()
        self.status = GuestState.no_state.value
        self.progress = 0
        self.node_id = None
        self.cpu = None
        self.memory = None
        self.ip = None
        self.network = None
        self.manage_network = None
        self.vnc_port = None
        self.vnc_password = None
        self.xml = None
        self.ssh_keys_id = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'uuid': FilterFieldType.STR.value,
            'label': FilterFieldType.STR.value,
            'status': FilterFieldType.INT.value,
            'remark': FilterFieldType.STR.value,
            'node_id': FilterFieldType.INT.value,
            'ip': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['remark', 'cpu', 'memory', 'network', 'manage_network', 'vnc_password', 'ssh_keys_id']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'remark', 'node_id', 'ip']


class Disk(ORM):

    _table_name = 'disk'
    _primary_key = 'id'

    def __init__(self):
        super(Disk, self).__init__()
        self.id = 0
        self.uuid = None
        self.remark = None
        self.path = None
        self.size = None
        self.sequence = None
        self.state = DiskState.pending.value
        self.node_id = None
        self.format = 'qcow2'
        self.create_time = ji.Common.tus()
        self.guest_uuid = None
        self.iops = 0
        self.iops_rd = 0
        self.iops_wr = 0
        self.iops_max = 0
        self.iops_max_length = 0
        self.bps = 0
        self.bps_rd = 0
        self.bps_wr = 0
        self.bps_max = 0
        self.bps_max_length = 0

    def quota(self, config=None):

        from models import Config
        assert isinstance(config, Config)

        # 系统盘 IOPS 默认不计算增益
        if self.sequence != 0:
            self.iops = config.iops_base + config.iops_pre_unit * self.size
        else:
            self.iops = config.iops_base

        if self.iops > config.iops_cap:
            self.iops = config.iops_cap

        self.iops_max = config.iops_max
        self.iops_max_length = config.iops_max_length
        self.iops_rd = 0
        self.iops_wr = 0

        # 系统盘 BPS 默认不计算增益
        if self.sequence != 0:
            self.bps = config.bps_base + config.bps_pre_unit * self.size
        else:
            self.bps = config.bps_base

        if self.bps > config.bps_cap:
            self.bps = config.bps_cap

        self.bps_max = config.bps_max
        self.bps_max_length = config.bps_max_length
        self.bps_rd = 0
        self.bps_wr = 0

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'uuid': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value,
            'size': FilterFieldType.INT.value,
            'state': FilterFieldType.INT.value,
            'sequence': FilterFieldType.INT.value,
            'node_id': FilterFieldType.INT.value,
            'guest_uuid': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['node_id', 'sequence', 'state', 'guest_uuid']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['remark', 'size', 'guest_uuid', 'uuid', 'node_id']


class GuestMigrateInfo(ORM):

    _table_name = 'guest_migrate_info'
    _primary_key = 'id'

    def __init__(self):
        super(GuestMigrateInfo, self).__init__()
        self.id = 0
        self.uuid = None
        self.type = None
        self.time_elapsed = None
        self.time_remaining = None
        self.data_total = None
        self.data_processed = None
        self.data_remaining = None
        self.mem_total = None
        self.mem_processed = None
        self.mem_remaining = None
        self.file_total = None
        self.file_processed = None
        self.file_remaining = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'uuid': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []

