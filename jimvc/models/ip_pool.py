#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import jimit as ji
from IPy import IP, intToIp

from jimvc.models import FilterFieldType
from jimvc.models import ORM


__author__ = 'James Iter'
__date__ = '2018-12-15'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class IPPool(ORM):

    _table_name = 'ip_pool'
    _primary_key = 'id'

    def __init__(self):
        super(IPPool, self).__init__()
        self.id = 0
        self.start_ip = ''
        self.end_ip = ''
        self.netmask = ''
        self.gateway = ''
        self.dns1 = ''
        self.dns2 = ''
        self.name = ''
        self.activity = 0
        self.description = ''
        self.create_time = ji.Common.tus()

    @staticmethod
    def get_filter_keywords():
        return {
            'name': FilterFieldType.STR.value,
            'activity': FilterFieldType.INT.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return ['name']

    def ip_generator(self, occupied_ips=None):
        """
        # 可用 IP 生成器
        :param occupied_ips: 已分配的虚拟机 IP 列表
        :return: 返回一个可分配的 IP 地址，格式如 '192.168.1.1'
        """

        assert isinstance(occupied_ips, list)

        occupied_ips_dec = list()

        for occupied_ip in occupied_ips:
            occupied_ips_dec.append(int(IP(occupied_ip).strDec()))

        for ip_dec in range(int(IP(self.start_ip).strDec()), int(IP(self.end_ip).strDec()) + 1):
            if ip_dec in occupied_ips_dec:
                continue

            yield intToIp(ip_dec, 4)

    @staticmethod
    def vnc_port_generator(occupied_vnc_ports=None):
        assert isinstance(occupied_vnc_ports, list)

        for vnc_port in range(15900, 20000):
            if vnc_port in occupied_vnc_ports:
                continue

            yield vnc_port

    def check_ip(self):
        network_segment = IP(self.start_ip + '/' + self.netmask, make_net=True)

        ret = dict()
        # 起止IP必须在同一个网段中
        if IP(self.end_ip) not in network_segment:
            ret['state'] = ji.Common.exchange_state(41251)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        # 网关必须与将分配给Guest的IP，处于同一个网段中
        if IP(self.gateway) not in network_segment:
            ret['state'] = ji.Common.exchange_state(41252)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        # 网关不能是网络地址或广播地址
        if IP(self.gateway) in [network_segment[i] for i in (0, -1)]:
            ret['state'] = ji.Common.exchange_state(41253)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        # 当用户输入的起始IP为网络地址时，自动重置其为该网段中第一个可用IP
        if self.start_ip == network_segment[0].__str__():
            self.start_ip = intToIp((int(IP(self.start_ip).strDec()) + 1).__str__(), 4)

        # 当用户输入的结束IP为广播地址时，自动重置其为该网段中最后一个可用IP
        if self.end_ip == network_segment[-1].__str__():
            self.end_ip = intToIp((int(IP(self.end_ip).strDec()) - 1).__str__(), 4)

        # 起始的可用IP地址必须小于结束的可用IP地址
        if IP(self.start_ip) >= IP(self.end_ip):
            ret['state'] = ji.Common.exchange_state(41254)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        return True

