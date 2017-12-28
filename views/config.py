#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, request, abort
import requests


__author__ = 'James Iter'
__date__ = '2017/8/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_config',
    __name__,
    url_prefix='/config'
)


def show():
    host_url = request.host_url.rstrip('/')
    config_url = host_url + '/api/config'
    config_ret = requests.get(url=config_url, cookies=request.cookies)
    config_ret = json.loads(config_ret.content)

    # 检测 JimV 的配置是否已被初始化，只有未被初始化时，才展现初始化配置页面
    if config_ret['state']['code'] == '404':
        abort(404)

    return render_template('config_show.html', config_ret=config_ret)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        payload = {
            'jimv_edition': int(request.form.get('jimv_edition', 0)),
            'storage_mode': int(request.form.get('storage_mode')),
            'dfs_volume': request.form.get('dfs_volume'),
            'storage_path': request.form.get('storage_path'),
            'vm_network': request.form.get('vm_network'),
            'vm_manage_network': request.form.get('vm_manage_network'),
            'start_ip': request.form.get('start_ip'),
            'end_ip': request.form.get('end_ip'),
            'start_vnc_port': int(request.form.get('start_vnc_port')),
            'netmask': request.form.get('netmask'),
            'gateway': request.form.get('gateway'),
            'dns1': request.form.get('dns1'),
            'dns2': request.form.get('dns2'),
            'iops_base': int(request.form.get('iops_base', 1000)),
            'iops_pre_unit': int(request.form.get('iops_pre_unit', 6)),
            'iops_cap': int(request.form.get('iops_cap', 2000)),
            'iops_max': int(request.form.get('iops_max', 3000)),
            'iops_max_length': int(request.form.get('iops_max_length', 20)),
            # 200 MiB
            'bps_base': int(request.form.get('bps_base', 1024 * 1024 * 200)),
            # 0.1 MiB
            'bps_pre_unit': int(request.form.get('bps_pre_unit', 1024 * 1024 / 10)),
            # 500 MiB
            'bps_cap': int(request.form.get('bps_cap', 1024 * 1024 * 500)),
            # 1 GiB
            'bps_max': int(request.form.get('bps_max', 1024 * 1024 * 1024)),
            'bps_max_length': int(request.form.get('bps_max_length', 10))
        }

        url = host_url + '/api/config'
        headers = {'content-type': 'application/json'}
        config_ret = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        config_ret = json.loads(config_ret.content)
        return render_template('success.html', go_back_url='/', timeout=5000, title='提交成功',
                               message_title='初始化 JimV 请求已被接受',
                               message='JimV 已被初始化。页面将在5秒钟后自动跳转到实例列表页面！')

    else:
        url = host_url + '/api/config'
        config_ret = requests.get(url=url, cookies=request.cookies)
        config_ret = json.loads(config_ret.content)

        # 检测 JimV 的配置是否已被初始化，只有未被初始化时，才展现初始化配置页面
        if config_ret['state']['code'] == '404':
            return render_template('config_init.html')
        else:
            abort(404)

