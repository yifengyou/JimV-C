#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, url_for, request, redirect
import requests
from . import render


__author__ = 'James Iter'
__date__ = '2018/2/27'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'v_ssh_key',
    __name__,
    url_prefix='/ssh_key'
)

blueprints = Blueprint(
    'v_ssh_keys',
    __name__,
    url_prefix='/ssh_keys'
)


def show():
    url = url_for('api_ssh_keys.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in list(request.args.items()):
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render('ssh_keys_show.html', ssh_keys=ret['data']['ssh_keys'], paging=ret['data']['paging'],
                  page=ret['data']['page'], page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                  pages=ret['data']['pages'], order_by=ret['data']['order_by'], order=ret['data']['order'],
                  last_page=ret['data']['last_page'])


def create():
    return redirect(url_for('v_ssh_keys.show'))

