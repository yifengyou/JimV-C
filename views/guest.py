#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import random
from flask import Blueprint, render_template, url_for, request
import requests
import time

from models import Database as db
from models import Utils
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
    url = url_for('api_guests.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in request.args.items():
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render_template('guests_show.html', guests_ret=ret['data']['guests_ret'],
                           resource_path=request.path,
                           os_templates_image_mapping_by_id=ret['data']['os_templates_image_mapping_by_id'],
                           os_templates_profile_mapping_by_id=ret['data']['os_templates_profile_mapping_by_id'],
                           hosts_mapping_by_node_id=ret['data']['hosts_mapping_by_node_id'], page=ret['data']['page'],
                           page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                           pages=ret['data']['pages'], last_page=ret['data']['last_page'])


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
        if not Utils.port_is_opened(port=port):
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

