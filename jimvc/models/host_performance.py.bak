#!/usr/bin/env python
# -*- coding: utf-8 -*-


from filter import FilterFieldType
from orm import ORM


__author__ = 'James Iter'
__date__ = '2017/8/7'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class HostCPUMemory(ORM):

    _table_name = 'host_cpu_memory'
    _primary_key = 'id'

    def __init__(self):
        super(HostCPUMemory, self).__init__()
        self.id = 0
        self.node_id = None
        self.cpu_load = None
        self.memory_available = None
        self.timestamp = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'node_id': FilterFieldType.STR.value,
            'cpu_load': FilterFieldType.INT.value,
            'timestamp': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []


class HostTraffic(ORM):

    _table_name = 'host_traffic'
    _primary_key = 'id'

    def __init__(self):
        super(HostTraffic, self).__init__()
        self.id = 0
        self.node_id = None
        self.name = None
        self.rx_bytes = None
        self.rx_packets = None
        self.rx_errs = None
        self.rx_drop = None
        self.tx_bytes = None
        self.tx_packets = None
        self.tx_errs = None
        self.tx_drop = None
        self.timestamp = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'node_id': FilterFieldType.STR.value,
            'name': FilterFieldType.STR.value,
            'rx_bytes': FilterFieldType.INT.value,
            'rx_packets': FilterFieldType.INT.value,
            'tx_bytes': FilterFieldType.INT.value,
            'tx_packets': FilterFieldType.INT.value,
            'timestamp': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []


class HostDiskUsageIO(ORM):

    _table_name = 'host_disk_usage_io'
    _primary_key = 'id'

    def __init__(self):
        super(HostDiskUsageIO, self).__init__()
        self.id = 0
        self.node_id = None
        self.mountpoint = None
        self.used = None
        self.rd_req = None
        self.rd_bytes = None
        self.wr_req = None
        self.wr_bytes = None
        self.timestamp = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'node_id': FilterFieldType.STR.value,
            'mountpoint': FilterFieldType.STR.value,
            'used': FilterFieldType.INT.value,
            'rd_req': FilterFieldType.INT.value,
            'rd_bytes': FilterFieldType.INT.value,
            'wr_req': FilterFieldType.INT.value,
            'wr_bytes': FilterFieldType.INT.value,
            'timestamp': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []

