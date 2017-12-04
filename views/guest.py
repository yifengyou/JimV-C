#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import random
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil
import re
import socket
import time
from models import Database as db
from models.initialize import config


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_guest',
    __name__,
    url_prefix='/guest'
)

blueprints = Blueprint(
    'v_guests',
    __name__,
    url_prefix='/guests'
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

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    os_templates_ret = requests.get(url=os_templates_url, cookies=request.cookies)
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
        guests_boot_jobs_ret = requests.get(url=guests_boot_jobs_url, cookies=request.cookies)

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

    return render_template('guests_show.html', guests_ret=guests_ret, resource_path=resource_path,
                           os_templates_mapping_by_id=os_templates_mapping_by_id,
                           guests_boot_jobs_ret=guests_boot_jobs_ret, page=page,
                           page_size=page_size, keyword=keyword, pages=pages, last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        ability = request.form.get('ability')
        os_template_id = request.form.get('os_template_id')
        quantity = request.form.get('quantity')
        password = request.form.get('password')
        remark = request.form.get('remark')

        if not isinstance(ability, basestring):
            pass

        m = re.search('^(\d+)c(\d+)g$', ability.lower())
        if m is None:
            pass

        cpu = m.groups()[0]
        memory = m.groups()[1]

        payload = {
            "cpu": int(cpu),
            "memory": int(memory),
            "os_template_id": int(os_template_id),
            "quantity": int(quantity),
            "remark": remark,
            "password": password,
            "lease_term": 100
        }

        url = host_url + '/api/guest'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        j_r = json.loads(r.content)

        guests_url = host_url + url_for('api_guests.r_get_by_filter')
        guests_ret = requests.get(url=guests_url, cookies=request.cookies)
        guests_ret = json.loads(guests_ret.content)
        page_size = 10
        last_page = int(ceil(guests_ret['paging']['total'] / float(page_size)))

        return render_template('success.html',
                               go_back_url='/guests?page={0}&page_size={1}'.format(last_page, page_size),
                               timeout=10000, title='提交成功',
                               message_title='创建实例的请求已被接受',
                               message='您所提交的资源正在创建中。根据所提交资源的大小，需要等待几到十几分钟。页面将在10秒钟后自动跳转到实例列表页面！')

    else:
        os_template_url = host_url + url_for('api_os_templates.r_get_by_filter')
        os_template_ret = requests.get(url=os_template_url, cookies=request.cookies)
        os_template_ret = json.loads(os_template_ret.content)
        return render_template('guest_create.html', os_template_data=os_template_ret['data'])


def port_is_opened(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('0.0.0.0', port))
    if result == 0:
        return True
    else:
        return False


def vnc(uuid):
    host_url = request.host_url.rstrip('/')

    guest_url = host_url + url_for('api_guests.r_get', uuids=uuid)

    guest_ret = requests.get(url=guest_url, cookies=request.cookies)
    guest_ret = json.loads(guest_ret.content)

    port = random.randrange(50000, 60000)
    while True:
        if not port_is_opened(port=port):
            break

        port = random.randrange(50000, 60000)

    payload = {'listen_port': port, 'target_host': guest_ret['data']['on_host'],
               'target_port': guest_ret['data']['vnc_port']}
    db.r.rpush(config['ipc_queue'], json.dumps(payload, ensure_ascii=False))
    time.sleep(1)

    return render_template('vnc_lite.html', port=port, password=guest_ret['data']['vnc_password'])


def detail(uuid):
    host_url = request.host_url.rstrip('/')

    guest_url = host_url + url_for('api_guests.r_get', uuids=uuid)

    guest_ret = requests.get(url=guest_url, cookies=request.cookies)
    guest_ret = json.loads(guest_ret.content)

    os_template_url = host_url + url_for('api_os_templates.r_get', ids=guest_ret['data']['os_template_id'].__str__())

    os_template_ret = requests.get(url=os_template_url, cookies=request.cookies)
    os_template_ret = json.loads(os_template_ret.content)

    disks_url = host_url + url_for('api_disks.r_get_by_filter')
    disks_url = disks_url + '?filter=guest_uuid:in:' + guest_ret['data']['uuid']
    disks_ret = requests.get(url=disks_url, cookies=request.cookies)
    disks_ret = json.loads(disks_ret.content)

    return render_template('guest_detail.html', uuid=uuid, guest_ret=guest_ret, os_template_ret=os_template_ret,
                           disks_ret=disks_ret)


def success():
    return render_template('success.html', go_back_url='/guests', timeout=10000, title='提交成功',
                           message_title='创建实例的请求已被接受',
                           message='您所提交的资源正在创建中。根据所提交资源的大小，需要等待几到十几分钟。页面将在10秒钟后自动跳转到实例列表页面！')


def show_boot_job(uuid):
    host_url = request.host_url.rstrip('/')

    guest_url = host_url + url_for('api_guests.r_get', uuids=uuid)

    guest_ret = requests.get(url=guest_url, cookies=request.cookies)
    guest_ret = json.loads(guest_ret.content)

    guest_boot_jobs_url = host_url + url_for('api_guests.r_get_boot_jobs', uuids=uuid)
    guest_boot_jobs_ret = requests.get(url=guest_boot_jobs_url, cookies=request.cookies)
    guest_boot_jobs_ret = json.loads(guest_boot_jobs_ret.content)

    boot_jobs_url = host_url + url_for('api_boot_jobs.r_get_by_filter') + '?filter=id:in:' + \
        ','.join(guest_boot_jobs_ret['data']['boot_jobs'])

    boot_jobs_ret = requests.get(url=boot_jobs_url, cookies=request.cookies)
    boot_jobs_ret = json.loads(boot_jobs_ret.content)
    boot_jobs_mapping_by_id = dict()
    for boot_job in boot_jobs_ret['data']:
        boot_jobs_mapping_by_id[boot_job['id']] = boot_job

    return render_template('guest_boot_jobs.html', uuid=uuid, guest_ret=guest_ret,
                           guest_boot_jobs_ret=guest_boot_jobs_ret, boot_jobs_mapping_by_id=boot_jobs_mapping_by_id)


def show_guests_boot_jobs():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    host_url = request.host_url.rstrip('/')

    # 获取所有有启动作业的 Guests uuid
    uuids_of_all_had_boot_job_url = host_url + url_for('api_guests.r_get_uuids_of_all_had_boot_job')

    uuids_of_all_had_boot_job_ret = requests.get(url=uuids_of_all_had_boot_job_url, cookies=request.cookies)
    uuids_of_all_had_boot_job_ret = json.loads(uuids_of_all_had_boot_job_ret.content)
    guests_uuid = uuids_of_all_had_boot_job_ret['data']

    guests_boot_jobs_ret = {'data': dict()}

    if guests_uuid.__len__() > 0:
        # 获取指定 Guest 的启动作业 ID
        guests_boot_jobs_url = host_url + url_for('api_guests.r_get_boot_jobs',
                                                  uuids=','.join(guests_uuid[page_size * (page - 1): page_size * page]))
        guests_boot_jobs_ret = requests.get(url=guests_boot_jobs_url, cookies=request.cookies)

        guests_boot_jobs_ret = json.loads(guests_boot_jobs_ret.content)

        # 统一单个、多个的返回JSON格式
        if guests_uuid.__len__() == 1:
            guests_boot_jobs_ret['data'] = {guests_uuid[0]: guests_boot_jobs_ret['data']}

    # 取出 Guests 的启动作业 IDs，并去重
    guests_boot_jobs_id = list()
    for uuid, guest_boot_jobs in guests_boot_jobs_ret['data'].items():
        guests_boot_jobs_id.extend(guest_boot_jobs['boot_jobs'])

    guests_boot_jobs_id = list(set(guests_boot_jobs_id))

    # 获取指定启动作业ID 的启动作业
    boot_jobs_url = host_url + url_for('api_boot_jobs.r_get_by_filter') + '?filter=id:in:' + \
        ','.join(guests_boot_jobs_id)

    boot_jobs_ret = requests.get(url=boot_jobs_url, cookies=request.cookies)
    boot_jobs_ret = json.loads(boot_jobs_ret.content)

    # 启动作业 ID 与启动作业的映射
    boot_jobs_mapping_by_id = dict()
    for boot_job in boot_jobs_ret['data']:
        boot_jobs_mapping_by_id[boot_job['id']] = boot_job

    guests_url = host_url + url_for('api_guests.r_get_by_filter')

    guests_url = guests_url + '?filter=uuid:in:' + ','.join(guests_uuid[page_size * (page - 1): page_size * page])

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    # Guest uuid 与 Guest 的映射
    guests_mapping_by_uuid = dict()
    for guest in guests_ret['data']:
        guests_mapping_by_uuid[guest['uuid']] = guest

    os_templates_url = host_url + url_for('api_os_templates.r_get_by_filter')
    os_templates_ret = requests.get(url=os_templates_url, cookies=request.cookies)
    os_templates_ret = json.loads(os_templates_ret.content)

    # 模板与模板 ID 的映射
    os_templates_mapping_by_id = dict()
    for os_template in os_templates_ret['data']:
        os_templates_mapping_by_id[os_template['id']] = os_template

    paging_total = guests_uuid.__len__()

    last_page = int(ceil(paging_total / float(page_size)))
    if last_page == 0:
        last_page = 1

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

    return render_template('guests_boot_jobs.html', guests_boot_jobs_ret=guests_boot_jobs_ret,
                           boot_jobs_mapping_by_id=boot_jobs_mapping_by_id,
                           guests_mapping_by_uuid=guests_mapping_by_uuid,
                           os_templates_mapping_by_id=os_templates_mapping_by_id, page=page, page_size=page_size,
                           pages=pages, last_page=last_page, paging_total=paging_total)

