#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, url_for, request
import requests
from . import render


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

        for k, v in list(request.args.items()):
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render('disks_show.html', disks=ret['data']['disks'],
                  resource_path=request.path,
                  hosts_mapping_by_node_id=ret['data']['hosts_mapping_by_node_id'],
                  page=ret['data']['page'], page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                  pages=ret['data']['pages'], order_by=ret['data']['order_by'], order=ret['data']['order'],
                  last_page=ret['data']['last_page'], paging=ret['data']['paging'],
                  show_area=ret['data']['show_area'], config=ret['data']['config'],
                  show_on_host=ret['data']['show_on_host'])


def create():
    return render('disk_create.html')


def detail(uuid):
    disk_detail_url = url_for('api_disk.r_detail', uuid=uuid, _external=True)
    disk_detail_ret = requests.get(url=disk_detail_url, cookies=request.cookies)
    disk_detail_ret = json.loads(disk_detail_ret.content)

    return render('disk_detail.html', uuid=uuid, guest=disk_detail_ret['data']['guest'],
                  os_template_image=disk_detail_ret['data']['os_template_image'],
                  disk=disk_detail_ret['data']['disk'],
                  config=disk_detail_ret['data']['config'])

