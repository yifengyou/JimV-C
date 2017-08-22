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
    args = list()
    resource_path = request.path

    host_url = request.host_url.rstrip('/')

    hosts_url = host_url + url_for('api_hosts.r_get_by_filter')
    guests_distribute_count_url = host_url + url_for('api_guests.r_distribute_count')

    hosts_ret = requests.get(url=hosts_url)
    hosts_ret = json.loads(hosts_ret.content)

    guests_distribute_count_ret = requests.get(url=guests_distribute_count_url)
    guests_distribute_count_ret = json.loads(guests_distribute_count_ret.content)

    hosts_sum = {'cpu': 0, 'memory': 0}

    for host in hosts_ret['data']:
        hosts_sum['cpu'] += host['cpu']
        hosts_sum['memory'] += host['memory']

    return render_template('dashboard.html', hosts_sum=hosts_sum, resource_path=resource_path,
                           guests_distribute_count_ret=guests_distribute_count_ret)

