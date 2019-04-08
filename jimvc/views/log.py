#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, url_for, request
import requests
from . import render


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
    url = url_for('api_logs.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in request.args.items():
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies, verify=False)
    ret = json.loads(ret.content)

    return render('logs.html', logs=ret['data']['logs'],
                  resource_path=request.path, page=ret['data']['page'],
                  page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                  paging=ret['data']['paging'],
                  pages=ret['data']['pages'], order_by=ret['data']['order_by'], order=ret['data']['order'],
                  last_page=ret['data']['last_page'])


