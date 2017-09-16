#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request, redirect
import requests
from math import ceil


__author__ = 'James Iter'
__date__ = '2017/7/11'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_os_template',
    __name__,
    url_prefix='/os_template'
)

blueprints = Blueprint(
    'v_os_templates',
    __name__,
    url_prefix='/os_templates'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    guest_uuid = request.args.get('guest_uuid', None)
    sequence = request.args.get('sequence', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', None)
    filters = list()
    resource_path = request.path

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    if guest_uuid is not None:
        filters.append('guest_uuid:in:' + guest_uuid.__str__())

    if sequence is not None:
        filters.append('sequence:in:' + sequence.__str__())

    if order_by is not None:
        args.append('order_by=' + order_by)

    if order is not None:
        args.append('order=' + order)

    if filters.__len__() > 0:
        args.append('filter=' + ','.join(filters))

    host_url = request.host_url.rstrip('/')

    os_templates_url = host_url + url_for('api_os_templates.r_get_by_filter')
    if keyword is not None:
        os_templates_url = host_url + url_for('api_os_templates.r_content_search')

    boot_job_url = host_url + url_for('api_boot_jobs.r_get_by_filter')

    if args.__len__() > 0:
        os_templates_url = os_templates_url + '?' + '&'.join(args)

    os_templates_ret = requests.get(url=os_templates_url, cookies=request.cookies)
    os_templates_ret = json.loads(os_templates_ret.content)

    boot_jobs_ret = requests.get(url=boot_job_url, cookies=request.cookies)
    boot_jobs_ret = json.loads(boot_jobs_ret.content)
    boot_jobs_mapping_by_id = dict()
    for boot_job in boot_jobs_ret['data']:
        boot_jobs_mapping_by_id[boot_job['id']] = boot_job

    last_page = int(ceil(os_templates_ret['paging']['total'] / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    return render_template('os_templates_show.html', os_templates_ret=os_templates_ret,
                           boot_jobs_mapping_by_id=boot_jobs_mapping_by_id, resource_path=resource_path,
                           page=page, page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        label = request.form.get('label')
        path = request.form.get('path')
        icon = request.form.get('icon')
        boot_job_id = request.form.get('boot_job_id')

        payload = {
            "label": label,
            "path": path,
            "active": True,
            "icon": icon,
            "boot_job_id": int(boot_job_id)
        }

        url = host_url + '/api/os_template'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        j_r = json.loads(r.content)
        return render_template('success.html', go_back_url='/os_templates', timeout=10000, title='提交成功',
                               message_title='添加模板的请求已被接受',
                               message='您所提交的模板已创建。页面将在10秒钟后自动跳转到模板列表页面！')

    else:
        return redirect(url_for('v_os_templates.show'))



