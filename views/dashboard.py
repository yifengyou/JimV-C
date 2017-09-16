#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests


__author__ = 'James Iter'
__date__ = '2017/8/17'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_dashboard',
    __name__,
    url_prefix='/'
)


def show():
    resource_path = request.path

    host_url = request.host_url.rstrip('/')

    hosts_url = host_url + url_for('api_hosts.r_get_by_filter')
    guests_distribute_count_url = host_url + url_for('api_guests.r_distribute_count')
    disks_distribute_count_url = host_url + url_for('api_disks.r_distribute_count')
    guests_current_top_10_url = host_url + url_for('api_performance.r_current_top_10')
    hosts_current_top_10_url = host_url + url_for('api_host_performance.r_current_top_10')

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

    guests_url = host_url + url_for('api_guests.r_get_by_filter')

    guests_uuid = list()

    for k, v in guests_current_top_10_ret['data'].items():
        for item in v:
            if 'guest_uuid' not in item:
                break

            if item['guest_uuid'] not in guests_uuid:
                guests_uuid.append(item['guest_uuid'])

    guests_url = guests_url + '?filter=uuid:in:' + ','.join(guests_uuid)

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    # Guest uuid 与 Guest 的映射
    guests_mapping_by_uuid = dict()
    for guest in guests_ret['data']:
        guests_mapping_by_uuid[guest['uuid']] = guest

    disks_url = host_url + url_for('api_disks.r_get_by_filter')

    disks_uuid = list()
    for k, v in guests_current_top_10_ret['data'].items():
        for item in v:
            if 'disk_uuid' not in item:
                break

            if item['disk_uuid'] not in disks_uuid:
                disks_uuid.append(item['disk_uuid'])

    disks_url = disks_url + '?filter=uuid:in:' + ','.join(disks_uuid)

    disks_ret = requests.get(url=disks_url, cookies=request.cookies)
    disks_ret = json.loads(disks_ret.content)

    # Disk uuid 与 Disk 的映射
    disks_mapping_by_uuid = dict()
    for disk in disks_ret['data']:
        disks_mapping_by_uuid[disk['uuid']] = disk

    hosts_current_top_10_ret = requests.get(url=hosts_current_top_10_url, cookies=request.cookies)
    hosts_current_top_10_ret = json.loads(hosts_current_top_10_ret.content)
    hosts_current_top_10_ret['data']['memory_rate'] = hosts_current_top_10_ret['data']['cpu_load']

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

    return render_template('dashboard.html', hosts_sum=hosts_sum, resource_path=resource_path,
                           guests_distribute_count_ret=guests_distribute_count_ret,
                           disks_distribute_count_ret=disks_distribute_count_ret,
                           guests_current_top_10_ret=guests_current_top_10_ret,
                           guests_mapping_by_uuid=guests_mapping_by_uuid, disks_mapping_by_uuid=disks_mapping_by_uuid,
                           hosts_current_top_10_ret=hosts_current_top_10_ret,
                           hosts_mapping_by_node_id=hosts_mapping_by_node_id)

