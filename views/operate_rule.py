#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request, redirect
import requests
from math import ceil

from models.status import OperateRuleKind, BootJobUseFor

__author__ = 'James Iter'
__date__ = '2017/7/17'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_operate_rule',
    __name__,
    url_prefix='/operate_rule'
)

blueprints = Blueprint(
    'v_operate_rules',
    __name__,
    url_prefix='/operate_rules'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    boot_job_id = request.args.get('boot_job_id', None)
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

    if boot_job_id is not None:
        filters.append('boot_job_id:in:' + boot_job_id.__str__())

    if order_by is not None:
        args.append('order_by=' + order_by)

    if order is not None:
        args.append('order=' + order)

    if filters.__len__() > 0:
        args.append('filter=' + ','.join(filters))

    host_url = request.host_url.rstrip('/')

    operate_rules_url = host_url + url_for('api_operate_rules.r_get_by_filter')
    if keyword is not None:
        operate_rules_url = host_url + url_for('api_operate_rules.r_content_search')

    boot_jobs_url = host_url + url_for('api_boot_jobs.r_get_by_filter')

    if args.__len__() > 0:
        operate_rules_url = operate_rules_url + '?' + '&'.join(args)

    operate_rules_ret = requests.get(url=operate_rules_url)
    operate_rules_ret = json.loads(operate_rules_ret.content)

    system_level_ids = list()

    boot_jobs_ret = requests.get(url=boot_jobs_url)
    boot_jobs_ret = json.loads(boot_jobs_ret.content)
    boot_jobs_mapping_by_id = dict()
    for boot_job in boot_jobs_ret['data']:
        boot_jobs_mapping_by_id[boot_job['id']] = boot_job

        if boot_job['use_for'] == BootJobUseFor.system.value:
            system_level_ids.append(boot_job['id'])

    for i, operate_rule in enumerate(operate_rules_ret['data']):
        # 去除系统级的启动作业。系统级的启动作业不展示给使用者。
        if operate_rule['boot_job_id'] in system_level_ids:
            del operate_rules_ret['data'][i]

    last_page = int(ceil(operate_rules_ret['paging']['total'] / float(page_size)))
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

    return render_template('operate_rule_show.html', operate_rules_ret=operate_rules_ret,
                           boot_jobs_mapping_by_id=boot_jobs_mapping_by_id, resource_path=resource_path,
                           page=page, page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        boot_job_id = int(request.form.get('boot_job_id'))
        kind = int(request.form.get('kind'))
        sequence = int(request.form.get('sequence'))

        payload = {
            "boot_job_id": boot_job_id,
            "kind": kind,
            "sequence": sequence
        }

        if kind == OperateRuleKind.cmd.value:
            payload['command'] = request.form.get('command', '')

        else:
            payload['path'] = request.form.get('path', '')
            payload['content'] = request.form.get('content', '')

        url = host_url + '/api/operate_rule'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)
        return render_template('success.html', go_back_url='/operate_rules', timeout=10000, title='提交成功',
                               message_title='添加启动作业操作细则的请求已被接受',
                               message='您所提交的启动作业操作细则已创建。页面将在10秒钟后自动跳转到模板列表页面！')

    else:
        return redirect(url_for('v_operate_rules.show'))


