#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, url_for, request
import requests
from . import render


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

        for k, v in list(request.args.items()):
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render('guests_show.html', guests=ret['data']['guests'],
                  resource_path=request.path,
                  os_templates_image_mapping_by_id=ret['data']['os_templates_image_mapping_by_id'],
                  os_templates_profile_mapping_by_id=ret['data']['os_templates_profile_mapping_by_id'],
                  hosts_mapping_by_node_id=ret['data']['hosts_mapping_by_node_id'], page=ret['data']['page'],
                  page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                  paging=ret['data']['paging'], pages=ret['data']['pages'], last_page=ret['data']['last_page'])


def vnc(uuid):
    vnc_url = url_for('api_guest.r_vnc', uuid=uuid, _external=True)
    vnc_ret = requests.get(url=vnc_url, cookies=request.cookies)
    vnc_ret = json.loads(vnc_ret.content)

    return render('vnc_lite.html', port=vnc_ret['data']['port'], password=vnc_ret['data']['vnc_password'])


def detail(uuid):
    guest_detail_url = url_for('api_guest.r_detail', uuid=uuid, _external=True)
    guest_detail_ret = requests.get(url=guest_detail_url, cookies=request.cookies)
    guest_detail_ret = json.loads(guest_detail_ret.content)

    return render('guest_detail.html', uuid=uuid, guest=guest_detail_ret['data']['guest'],
                  os_template_image=guest_detail_ret['data']['os_template_image'],
                  os_templates_profile_mapping_by_id=
                  guest_detail_ret['data']['os_templates_profile_mapping_by_id'],
                  hosts_mapping_by_node_id=guest_detail_ret['data']['hosts_mapping_by_node_id'],
                  disks=guest_detail_ret['data']['disks'], config=guest_detail_ret['data']['config'])


def create():
        hosts_url = url_for('api_hosts.r_get_by_filter', alive=True, _external=True)
        hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
        hosts_ret = json.loads(hosts_ret.content)

        return render('guest_create.html', hosts_ret=hosts_ret)

