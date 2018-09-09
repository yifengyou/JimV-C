#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import copy
import jimit as ji
from flask import url_for, request, Blueprint

from models import Utils


__author__ = 'James Iter'
__date__ = '2018/9/9'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_dashboard',
    __name__,
    url_prefix='/api/dashboard'
)

blueprints = Blueprint(
    'api_dashboards',
    __name__,
    url_prefix='/api/dashboards'
)


@Utils.dumps2response
def r_show():
    # alive 的布尔值 True，在 url 中传输前，会自动转换为字符串 'True'
    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True, alive=True)
    guests_distribute_count_url = url_for('api_guests.r_distribute_count', _external=True)
    disks_distribute_count_url = url_for('api_disks.r_distribute_count', _external=True)
    guests_current_top_10_url = url_for('api_guest_performance.r_current_top_10', _external=True)
    hosts_current_top_10_url = url_for('api_host_performance.r_current_top_10', _external=True)

    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    # Host node_id 与 Host 的映射
    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    guests_distribute_count_ret = requests.get(url=guests_distribute_count_url, cookies=request.cookies)
    guests_distribute_count_ret = json.loads(guests_distribute_count_ret.content)

    disks_distribute_count_ret = requests.get(url=disks_distribute_count_url, cookies=request.cookies)
    disks_distribute_count_ret = json.loads(disks_distribute_count_ret.content)

    guests_current_top_10_ret = requests.get(url=guests_current_top_10_url, cookies=request.cookies)
    guests_current_top_10_ret = json.loads(guests_current_top_10_ret.content)

    guests_uuid = list()

    for k, v in guests_current_top_10_ret['data'].items():
        for item in v:
            if 'guest_uuid' not in item:
                break

            if item['guest_uuid'] not in guests_uuid:
                guests_uuid.append(item['guest_uuid'])

    guests_url = url_for('api_guests.r_get_by_filter', _external=True, filter='uuid:in:' + ','.join(guests_uuid))

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    # Guest uuid 与 Guest 的映射
    guests_mapping_by_uuid = dict()
    for guest in guests_ret['data']:
        guests_mapping_by_uuid[guest['uuid']] = guest

    disks_uuid = list()
    for k, v in guests_current_top_10_ret['data'].items():
        for item in v:
            if 'disk_uuid' not in item:
                break

            if item['disk_uuid'] not in disks_uuid:
                disks_uuid.append(item['disk_uuid'])

    disks_url = url_for('api_disks.r_get_by_filter', _external=True, filter='uuid:in:' + ','.join(disks_uuid))

    disks_ret = requests.get(url=disks_url, cookies=request.cookies)
    disks_ret = json.loads(disks_ret.content)

    # Disk uuid 与 Disk 的映射
    disks_mapping_by_uuid = dict()
    for disk in disks_ret['data']:
        disks_mapping_by_uuid[disk['uuid']] = disk

    hosts_current_top_10_ret = requests.get(url=hosts_current_top_10_url, cookies=request.cookies)
    hosts_current_top_10_ret = json.loads(hosts_current_top_10_ret.content)
    hosts_current_top_10_ret['data']['memory_rate'] = copy.copy(hosts_current_top_10_ret['data']['cpu_load'])

    for i in range(hosts_current_top_10_ret['data']['memory_rate'].__len__()):
        memory_total = hosts_mapping_by_node_id[hosts_current_top_10_ret['data']['memory_rate'][i]['node_id']]['memory']
        memory_available = hosts_current_top_10_ret['data']['memory_rate'][i]['memory_available']
        memory_used = memory_total - memory_available
        hosts_current_top_10_ret['data']['memory_rate'][i]['memory_rate'] = int(memory_used / float(memory_total) * 100)

    hosts_current_top_10_ret['data']['memory_rate'].sort(key=lambda _k: _k['memory_rate'], reverse=True)

    hosts_sum = {'cpu': 0, 'memory': 0}

    for host in hosts_ret['data']:
        hosts_sum['cpu'] += host['cpu']
        hosts_sum['memory'] += host['memory']

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'hosts_sum': hosts_sum,
        'guests_distribute_count_ret': guests_distribute_count_ret,
        'disks_distribute_count_ret': disks_distribute_count_ret,
        'guests_current_top_10_ret': guests_current_top_10_ret,
        'guests_mapping_by_uuid': guests_mapping_by_uuid,
        'disks_mapping_by_uuid': disks_mapping_by_uuid,
        'hosts_current_top_10_ret': hosts_current_top_10_ret,
        'hosts_mapping_by_node_id': hosts_mapping_by_node_id
    }

    return ret

