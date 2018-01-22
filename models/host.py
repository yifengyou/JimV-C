#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import g

from initialize import app
from models import Database as db


__author__ = 'James Iter'
__date__ = '2017/9/19'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Host(object):

    def __init__(self):
        pass

    @staticmethod
    def alive_check(v):
        """
        JimV-C 2 秒更新一次宿主机信息，这里以 5 秒内没收到更新，作为判断宿主机是否在线的标准
        """

        if 'timestamp' not in v:
            return v

        v['alive'] = False
        if v['timestamp'] + 5 >= g.ts:
            v['alive'] = True

        return v

    @staticmethod
    def set_allocation_mode(hosts_name=None, random=True):
        if not isinstance(hosts_name, list):
            raise ValueError('The hosts_name must be a list.')

        if random:
            db.r.sadd(app.config['compute_nodes_of_allocation_by_nonrandom'], *hosts_name)

        else:
            db.r.srem(app.config['compute_nodes_of_allocation_by_nonrandom'], *hosts_name)

    @classmethod
    def get_all(cls):

        ret = list()
        compute_nodes_of_allocation_by_nonrandom = \
            list(db.r.smembers(app.config['compute_nodes_of_allocation_by_nonrandom']))

        for k, v in db.r.hgetall(app.config['hosts_info']).items():
            v = json.loads(v)
            v = cls.alive_check(v)
            v['node_id'] = k

            if v['hostname'] in compute_nodes_of_allocation_by_nonrandom:
                v['nonrandom'] = True
            else:
                v['nonrandom'] = False

            ret.append(v)

        if ret.__len__() > 1:
            ret.sort(key=lambda _k: _k['boot_time'])

        return ret

    @classmethod
    def get_available_hosts(cls, nonrandom=None):
        """
        :param nonrandom: {None, True, False}
            None for all;
            False for host can be allocation guest by random;
            True on the contrary.
        :return:
        """

        hosts = list()

        for host in cls.get_all():

            if not host['alive']:
                continue

            if nonrandom is not None and host['nonrandom'] != nonrandom:
                continue

            host['system_load_per_cpu'] = float(host['system_load'][0]) / host['cpu']
            hosts.append(host)

        hosts.sort(key=lambda _k: _k['system_load_per_cpu'])

        return hosts
