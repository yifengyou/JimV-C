#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil
from models.status import StorageMode


__author__ = 'James Iter'
__date__ = '2017/6/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_disk',
    __name__,
    url_prefix='/disk'
)

blueprints = Blueprint(
    'v_disks',
    __name__,
    url_prefix='/disks'
)


def show():
    url = url_for('api_disks.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in request.args.items():
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render_template('disks_show.html', disks=ret['data']['disks'],
                           resource_path=request.path,
                           hosts_mapping_by_node_id=ret['data']['hosts_mapping_by_node_id'],
                           page=ret['data']['page'], page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                           pages=ret['data']['pages'], order_by=ret['data']['order_by'], order=ret['data']['order'],
                           last_page=ret['data']['last_page'], paging=ret['data']['paging'],
                           show_area=ret['data']['show_area'], config=ret['data']['config'],
                           show_on_host=ret['data']['show_on_host'])


def create():
    return render_template('disk_create.html')


def detail(uuid):
    host_url = request.host_url.rstrip('/')

    disk_url = host_url + url_for('api_disks.r_get', uuids=uuid)

    disk_ret = requests.get(url=disk_url, cookies=request.cookies)
    disk_ret = json.loads(disk_ret.content)

    guest_ret = None
    os_template_image_ret = None

    config_url = host_url + url_for('api_config.r_get')
    config_ret = requests.get(url=config_url, cookies=request.cookies)
    config_ret = json.loads(config_ret.content)

    if disk_ret['data']['sequence'] != -1:
        guest_url = host_url + url_for('api_guests.r_get', uuids=disk_ret['data']['guest_uuid'])

        guest_ret = requests.get(url=guest_url, cookies=request.cookies)
        guest_ret = json.loads(guest_ret.content)

        os_template_image_url = host_url + url_for('api_os_templates_image.r_get',
                                                   ids=guest_ret['data']['os_template_image_id'].__str__())

        os_template_image_ret = requests.get(url=os_template_image_url, cookies=request.cookies)
        os_template_image_ret = json.loads(os_template_image_ret.content)

    return render_template('disk_detail.html', uuid=uuid, guest_ret=guest_ret,
                           os_template_image_ret=os_template_image_ret, disk_ret=disk_ret, config_ret=config_ret)


