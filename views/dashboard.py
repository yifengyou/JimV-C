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

    hosts_ret = requests.get(url=hosts_url)
    hosts_ret = json.loads(hosts_ret.content)

    guests_distribute_count_ret = requests.get(url=guests_distribute_count_url)
    guests_distribute_count_ret = json.loads(guests_distribute_count_ret.content)

    disks_distribute_count_ret = requests.get(url=disks_distribute_count_url)
    disks_distribute_count_ret = json.loads(disks_distribute_count_ret.content)

    guests_current_top_10_ret = requests.get(url=guests_current_top_10_url)
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

    guests_ret = requests.get(url=guests_url)
    guests_ret = json.loads(guests_ret.content)

    # Guest uuid 与 Guest 的映射
    guests_mapping_by_uuid = dict()
    for guest in guests_ret['data']:
        guests_mapping_by_uuid[guest['uuid']] = guest

    hosts_sum = {'cpu': 0, 'memory': 0}

    for host in hosts_ret['data']:
        hosts_sum['cpu'] += host['cpu']
        hosts_sum['memory'] += host['memory']

    return render_template('dashboard.html', hosts_sum=hosts_sum, resource_path=resource_path,
                           guests_distribute_count_ret=guests_distribute_count_ret,
                           disks_distribute_count_ret=disks_distribute_count_ret,
                           guests_current_top_10_ret=guests_current_top_10_ret,
                           guests_mapping_by_uuid=guests_mapping_by_uuid)

