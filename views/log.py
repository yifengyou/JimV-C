#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil


__author__ = 'James Iter'
__date__ = '2017/7/9'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_log',
    __name__,
    url_prefix='/log'
)

blueprints = Blueprint(
    'v_logs',
    __name__,
    url_prefix='/logs'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', 'desc')
    resource_path = request.path

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

    logs_url = host_url + url_for('api_logs.r_get_by_filter')
    if keyword is not None:
        logs_url = host_url + url_for('api_logs.r_content_search')

    if args.__len__() > 0:
        logs_url = logs_url + '?' + '&'.join(args)

    logs_ret = requests.get(url=logs_url)
    logs_ret = json.loads(logs_ret.content)

    last_page = int(ceil(logs_ret['paging']['total'] / float(page_size)))
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

    return render_template('logs.html', logs_ret=logs_ret, resource_path=resource_path, page=page,
                           page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page)


