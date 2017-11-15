#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import jimit as ji
from IPy import IP, intToIp

from initialize import app
from models import Database as db
from models import ORM
from models import status


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
        self.start_ip = ''
        self.end_ip = ''
        self.start_vnc_port = None
        self.netmask = ''
        self.gateway = ''
        self.dns1 = ''
        self.dns2 = ''

    @staticmethod
    def get_filter_keywords():
        return {}

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []

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

    def generate_available_ip2set(self):
        # 删除现有的可用IP集合
        db.r.delete(app.config['ip_available_set'])

        for ip_dec in range(int(IP(self.start_ip).strDec()), int(IP(self.end_ip).strDec()) + 1):
            db.r.sadd(app.config['ip_available_set'], intToIp(ip_dec, 4))

    def generate_available_vnc_port(self):
        # 删除现有的可用 vnc 端口集合
        db.r.delete(app.config['vnc_port_available_set'])

        i = 0
        # 借用可用 IP 范围生成需要的 vnc 端口集合
        for ip_dec in range(int(IP(self.start_ip).strDec()), int(IP(self.end_ip).strDec()) + 1):
            i += 1
            db.r.sadd(app.config['vnc_port_available_set'], self.start_vnc_port + i)

    def update_global_config(self):
        db.r.hmset(app.config['global_config'], self.__dict__)

