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

        coupler_length = 5

        if 'timestamp' not in v:
            return v

        v['alive'] = False
        if v['timestamp'] + coupler_length >= g.ts:
            v['alive'] = True

        if 'threads_status' not in v:
            v['threads_status'] = {
                'instruction_process_engine': {
                    'timestamp': 0,
                    'alive': False
                },
                'host_state_report_engine': {
                    'timestamp': 0,
                    'alive': False
                },
                'guest_creating_progress_report_engine': {
                    'timestamp': 0,
                    'alive': False
                },
                'guest_performance_collection_engine': {
                    'timestamp': 0,
                    'alive': False
                },
                'host_performance_collection_engine': {
                    'timestamp': 0,
                    'alive': False
                }
            }

        if v['threads_status']['instruction_process_engine']['timestamp'] + coupler_length >= g.ts:
            v['threads_status']['instruction_process_engine']['alive'] = True

        if v['threads_status']['host_state_report_engine']['timestamp'] + coupler_length >= g.ts:
            v['threads_status']['host_state_report_engine']['alive'] = True

        if v['threads_status']['guest_creating_progress_report_engine']['timestamp'] + coupler_length >= g.ts:
            v['threads_status']['guest_creating_progress_report_engine']['alive'] = True

        if v['threads_status']['guest_performance_collection_engine']['timestamp'] + coupler_length >= g.ts:
            v['threads_status']['guest_performance_collection_engine']['alive'] = True

        if v['threads_status']['host_performance_collection_engine']['timestamp'] + coupler_length >= g.ts:
            v['threads_status']['host_performance_collection_engine']['alive'] = True

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

    @staticmethod
    def get_lightest_host():
        # 负载最小的宿主机
        lightest_host = None
        for k, v in db.r.hgetall(app.config['hosts_info']).items():
            v = json.loads(v)

            if lightest_host is None:
                lightest_host = v

            if float(lightest_host['system_load'][0]) / lightest_host['cpu'] > \
                    float(v['system_load'][0]) / v['cpu']:
                lightest_host = v

        return lightest_host
