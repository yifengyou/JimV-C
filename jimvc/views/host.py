#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, url_for, request
import requests
from . import render


__author__ = 'James Iter'
__date__ = '2017/8/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_host',
    __name__,
    url_prefix='/host'
)

blueprints = Blueprint(
    'v_hosts',
    __name__,
    url_prefix='/hosts'
)


def show():
    url = url_for('api_hosts.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in list(request.args.items()):
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render('hosts_show.html', hosts=ret['data']['hosts'], resource_path=request.path,
                  keyword=ret['data']['keyword'])


def detail(node_id):
    host_url = url_for('api_hosts.r_get', nodes_id=node_id, _external=True)

    host_ret = requests.get(url=host_url, cookies=request.cookies)
    host_ret = json.loads(host_ret.content)

    return render('host_detail.html', node_id=node_id, host=host_ret['data'])

