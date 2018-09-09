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
    url = url_for('api_dashboard.r_show', _external=True)
    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render_template('dashboard.html', hosts_sum=ret['data']['hosts_sum'],
                           guests_distribute_count_ret=ret['data']['guests_distribute_count_ret'],
                           disks_distribute_count_ret=ret['data']['disks_distribute_count_ret'],
                           guests_current_top_10_ret=ret['data']['guests_current_top_10_ret'],
                           guests_mapping_by_uuid=ret['data']['guests_mapping_by_uuid'],
                           disks_mapping_by_uuid=ret['data']['disks_mapping_by_uuid'],
                           hosts_current_top_10_ret=ret['data']['hosts_current_top_10_ret'],
                           hosts_mapping_by_node_id=ret['data']['hosts_mapping_by_node_id'])

