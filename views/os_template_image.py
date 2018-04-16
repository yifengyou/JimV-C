#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request, redirect
import requests
from math import ceil


__author__ = 'James Iter'
__date__ = '2018/2/5'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'v_os_template_image',
    __name__,
    url_prefix='/os_template_image'
)

blueprints = Blueprint(
    'v_os_templates_image',
    __name__,
    url_prefix='/os_templates_image'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', None)

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    if order_by is not None:
        args.append('order_by=' + order_by)

    if order is not None:
        args.append('order=' + order)

    host_url = request.host_url.rstrip('/')

    os_templates_image_url = host_url + url_for('api_os_templates_image.r_get_by_filter')
    if keyword is not None:
        os_templates_image_url = host_url + url_for('api_os_templates_image.r_content_search')

    os_templates_profile_url = host_url + url_for('api_os_templates_profile.r_get_by_filter')

    if args.__len__() > 0:
        os_templates_image_url = os_templates_image_url + '?' + '&'.join(args)

    os_templates_image_ret = requests.get(url=os_templates_image_url, cookies=request.cookies)
    os_templates_image_ret = json.loads(os_templates_image_ret.content)

    os_templates_profile_ret = requests.get(url=os_templates_profile_url, cookies=request.cookies)
    os_templates_profile_ret = json.loads(os_templates_profile_ret.content)
    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile_ret['data']:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

    last_page = int(ceil(os_templates_image_ret['paging']['total'] / float(page_size)))
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

    return render_template('os_templates_image_show.html', os_templates_image_ret=os_templates_image_ret,
                           os_templates_profile_mapping_by_id=os_templates_profile_mapping_by_id,
                           page=page, page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        label = request.form.get('label')
        description = request.form.get('description', '')
        path = request.form.get('path')
        logo = request.form.get('logo')
        active = request.form.get('active', 1)
        os_template_profile_id = request.form.get('os_template_profile_id')
        kind = request.form.get('kind', 0)

        payload = {
            "label": label,
            "description": description,
            "path": path,
            "logo": logo,
            "active": active,
            "os_template_profile_id": int(os_template_profile_id),
            "kind": int(kind)
        }

        url = host_url + '/api/os_template_image'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        j_r = json.loads(r.content)
        if j_r['state']['code'] != '200':
            return render_template('failure.html',
                                   go_back_url='/os_templates_image',
                                   timeout=10000, title='创建失败',
                                   message_title='创建模板镜像失败',
                                   message=j_r['state']['sub']['zh-cn'])

        return render_template('success.html', go_back_url='/os_templates_image', timeout=10000, title='提交成功',
                               message_title='添加模板镜像的请求已被接受',
                               message='您所提交的模板镜像已创建。页面将在10秒钟后自动跳转到模板列表页面！')

    else:
        return redirect(url_for('v_os_templates_image.show'))
