#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil


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
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    resource_path = request.path

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    host_url = request.host_url.rstrip('/')

    guests_url = host_url + url_for('api_guests.r_get_by_filter')
    if keyword is not None:
        guests_url = host_url + url_for('api_guests.r_content_search')

    os_templates_url = host_url + url_for('api_os_templates.r_get_by_filter')

    if args.__len__() > 0:
        guests_url = guests_url + '?' + '&'.join(args)

    guests_ret = requests.get(url=guests_url)
    guests_ret = json.loads(guests_ret.content)

    os_templates_ret = requests.get(url=os_templates_url)
    os_templates_ret = json.loads(os_templates_ret.content)
    os_templates_mapping_by_id = dict()
    for os_template in os_templates_ret['data']:
        os_templates_mapping_by_id[os_template['id']] = os_template

    guests_uuid = list()

    for guest in guests_ret['data']:
        guests_uuid.append(guest['uuid'])

    guests_boot_jobs_ret = {'data': dict()}

    if guests_uuid.__len__() > 0:
        # 获取指定 Guest 的启动作业 ID
        guests_boot_jobs_url = host_url + url_for('api_guests.r_get_boot_jobs', uuids=','.join(guests_uuid))
        guests_boot_jobs_ret = requests.get(url=guests_boot_jobs_url)

        guests_boot_jobs_ret = json.loads(guests_boot_jobs_ret.content)

        # 统一单个、多个的返回JSON格式
        if guests_uuid.__len__() == 1:
            guests_boot_jobs_ret['data'] = {guests_uuid[0]: guests_boot_jobs_ret['data']}

    last_page = int(ceil(guests_ret['paging']['total'] / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page:
                break

    return render_template('config_show.html', guests_ret=guests_ret, resource_path=resource_path,
                           os_templates_mapping_by_id=os_templates_mapping_by_id,
                           guests_boot_jobs_ret=guests_boot_jobs_ret, page=page,
                           page_size=page_size, keyword=keyword, pages=pages, last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        payload = {
            'jimv_edition': request.form.get('jimv_edition', 0),
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
            'dns2': request.form.get('dns2')
        }

        url = host_url + '/api/config'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        return render_template('success.html', go_back_url='/', timeout=5000, title='提交成功',
                               message_title='初始化 JimV 请求已被接受',
                               message='JimV 已被初始化。页面将在5秒钟后自动跳转到实例列表页面！')

    else:
        return render_template('config_init.html')


def success():
    return render_template('success.html', go_back_url='/', timeout=5000, title='提交成功',
                           message_title='初始化 JimV 的请求已被接受',
                           message='JimV 已被初始化。页面将在5秒钟后自动跳转到实例列表页面！')


