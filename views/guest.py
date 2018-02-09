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

    hosts_url = host_url + url_for('api_hosts.r_get_by_filter')
    guests_url = host_url + url_for('api_guests.r_get_by_filter')
    if keyword is not None:
        guests_url = host_url + url_for('api_guests.r_content_search')

    os_templates_image_url = host_url + url_for('api_os_templates_image.r_get_by_filter')
    os_templates_profile_url = host_url + url_for('api_os_templates_profile.r_get_by_filter')

    if args.__len__() > 0:
        guests_url = guests_url + '?' + '&'.join(args)

    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    os_templates_image_ret = requests.get(url=os_templates_image_url, cookies=request.cookies)
    os_templates_image_ret = json.loads(os_templates_image_ret.content)
    os_templates_image_mapping_by_id = dict()
    for os_template_image in os_templates_image_ret['data']:
        os_templates_image_mapping_by_id[os_template_image['id']] = os_template_image

    os_templates_profile_ret = requests.get(url=os_templates_profile_url, cookies=request.cookies)
    os_templates_profile_ret = json.loads(os_templates_profile_ret.content)
    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile_ret['data']:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

    guests_uuid = list()

    for guest in guests_ret['data']:
        guests_uuid.append(guest['uuid'])

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
                           os_templates_image_mapping_by_id=os_templates_image_mapping_by_id,
                           os_templates_profile_mapping_by_id=os_templates_profile_mapping_by_id,
                           hosts_mapping_by_node_id=hosts_mapping_by_node_id, page=page,
                           page_size=page_size, keyword=keyword, pages=pages, last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        ability = request.form.get('ability')
        os_template_image_id = request.form.get('os_template_image_id')
        quantity = request.form.get('quantity')
        password = request.form.get('password')
        remark = request.form.get('remark')
        allocation_by_random = 'allocation_by_random' in request.form
        node_id = request.form.get('node_id')

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
            "os_template_image_id": int(os_template_image_id),
            "quantity": int(quantity),
            "remark": remark,
            "password": password,
            "lease_term": 100
        }

        if not allocation_by_random:
            payload['node_id'] = node_id

        url = host_url + '/api/guest'
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        j_r = json.loads(r.content)

        if j_r['state']['code'] != '200':
            return render_template('failure.html',
                                   go_back_url='/guests',
                                   timeout=10000, title='创建失败',
                                   message_title='创建实例失败',
                                   message=j_r['state']['sub']['zh-cn'])

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
        hosts_url = host_url + url_for('api_hosts.r_get_by_filter', alive=True)

        hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
        hosts_ret = json.loads(hosts_ret.content)

        return render_template('guest_create.html', hosts_ret=hosts_ret)


def port_is_opened(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('0.0.0.0', port))
    if result == 0:
        return True
    else:
        return False


def vnc(uuid):
    host_url = request.host_url.rstrip('/')

    hosts_url = host_url + url_for('api_hosts.r_get_by_filter')
    guest_url = host_url + url_for('api_guests.r_get', uuids=uuid)

    guest_ret = requests.get(url=guest_url, cookies=request.cookies)
    guest_ret = json.loads(guest_ret.content)

    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    port = random.randrange(50000, 60000)
    while True:
        if not port_is_opened(port=port):
            break

        port = random.randrange(50000, 60000)

    payload = {'listen_port': port, 'target_host': hosts_mapping_by_node_id[guest_ret['data']['node_id']]['hostname'],
               'target_port': guest_ret['data']['vnc_port']}
    db.r.rpush(config['ipc_queue'], json.dumps(payload, ensure_ascii=False))
    time.sleep(1)

    return render_template('vnc_lite.html', port=port, password=guest_ret['data']['vnc_password'])


def detail(uuid):
    host_url = request.host_url.rstrip('/')

    hosts_url = host_url + url_for('api_hosts.r_get_by_filter')
    guest_url = host_url + url_for('api_guests.r_get', uuids=uuid)

    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    guest_ret = requests.get(url=guest_url, cookies=request.cookies)
    guest_ret = json.loads(guest_ret.content)

    os_template_image_url = host_url + url_for('api_os_templates_image.r_get',
                                               ids=guest_ret['data']['os_template_image_id'].__str__())
    os_templates_profile_url = host_url + url_for('api_os_templates_profile.r_get_by_filter')

    os_template_image_ret = requests.get(url=os_template_image_url, cookies=request.cookies)
    os_template_image_ret = json.loads(os_template_image_ret.content)

    os_templates_profile_ret = requests.get(url=os_templates_profile_url, cookies=request.cookies)
    os_templates_profile_ret = json.loads(os_templates_profile_ret.content)
    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile_ret['data']:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

    disks_url = host_url + url_for('api_disks.r_get_by_filter', filter='guest_uuid:in:' + guest_ret['data']['uuid'])
    disks_ret = requests.get(url=disks_url, cookies=request.cookies)
    disks_ret = json.loads(disks_ret.content)

    url = host_url + '/api/config'
    config_ret = requests.get(url=url, cookies=request.cookies)
    config_ret = json.loads(config_ret.content)

    return render_template('guest_detail.html', uuid=uuid, guest_ret=guest_ret,
                           os_template_image_ret=os_template_image_ret,
                           os_templates_profile_mapping_by_id=os_templates_profile_mapping_by_id,
                           hosts_mapping_by_node_id=hosts_mapping_by_node_id,
                           disks_ret=disks_ret, config_ret=config_ret)


def success():
    return render_template('success.html', go_back_url='/guests', timeout=10000, title='提交成功',
                           message_title='创建实例的请求已被接受',
                           message='您所提交的资源正在创建中。根据所提交资源的大小，需要等待几到十几分钟。页面将在10秒钟后自动跳转到实例列表页面！')


