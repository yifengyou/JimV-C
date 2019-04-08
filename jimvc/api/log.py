#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from math import ceil
import jimit as ji

import requests
from flask import Blueprint, request, url_for

from jimvc.api.base import Base
from jimvc.models import Log
from jimvc.models import Rules
from jimvc.models import Utils


__author__ = 'James Iter'
__date__ = '2017/4/8'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_log',
    __name__,
    url_prefix='/api/log'
)

blueprints = Blueprint(
    'api_logs',
    __name__,
    url_prefix='/api/logs'
)


log_base = Base(the_class=Log, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_get(ids):
    return log_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return log_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return log_base.content_search()


@Utils.dumps2response
def r_show():
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

    logs_url = url_for('api_logs.r_get_by_filter', _external=True)
    if keyword is not None:
        logs_url = url_for('api_logs.r_content_search', _external=True)

    if args.__len__() > 0:
        logs_url = logs_url + '?' + '&'.join(args)

    logs_ret = requests.get(url=logs_url, cookies=request.cookies, verify=False)
    logs_ret = json.loads(logs_ret.content)

    last_page = int(ceil(logs_ret['paging']['total'] / float(page_size)))
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
    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'logs': logs_ret['data'],
        'paging': logs_ret['paging'],
        'page': page,
        'page_size': page_size,
        'keyword': keyword,
        'pages': pages,
        'last_page': last_page,
        'order_by': order_by,
        'order': order
    }

    return ret

