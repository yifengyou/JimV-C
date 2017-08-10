#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil


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
    if keyword is not None:
        hosts_url = host_url + url_for('api_hosts.r_content_search')

    if args.__len__() > 0:
        hosts_url = hosts_url + '?' + '&'.join(args)

    hosts_ret = requests.get(url=hosts_url)
    hosts_ret = json.loads(hosts_ret.content)

    return render_template('hosts_show.html', hosts_ret=hosts_ret, resource_path=resource_path, keyword=keyword)


