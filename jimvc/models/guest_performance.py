#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jimvc.models import ORM, FilterFieldType


__author__ = 'James Iter'
__date__ = '2017/6/28'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class GuestCPUMemory(ORM):

    _table_name = 'guest_cpu_memory'
    _primary_key = 'id'

    def __init__(self):
        super(GuestCPUMemory, self).__init__()
        self.id = 0
        self.guest_uuid = None
        self.cpu_load = None
        self.memory_available = None
        self.memory_rate = None
        self.timestamp = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'guest_uuid': FilterFieldType.STR.value,
            'cpu_load': FilterFieldType.INT.value,
            'memory_available': FilterFieldType.INT.value,
            'memory_rate': FilterFieldType.INT.value,
            'timestamp': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []


class GuestTraffic(ORM):

    _table_name = 'guest_traffic'
    _primary_key = 'id'

    def __init__(self):
        super(GuestTraffic, self).__init__()
        self.id = 0
        self.guest_uuid = None
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
            'guest_uuid': FilterFieldType.STR.value,
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


class GuestDiskIO(ORM):

    _table_name = 'guest_disk_io'
    _primary_key = 'id'

    def __init__(self):
        super(GuestDiskIO, self).__init__()
        self.id = 0
        self.disk_uuid = None
        self.rd_req = None
        self.rd_bytes = None
        self.wr_req = None
        self.wr_bytes = None
        self.timestamp = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'disk_uuid': FilterFieldType.STR.value,
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

