#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests


__author__ = 'James Iter'
__date__ = '2018/3/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'v_snapshot',
    __name__,
    url_prefix='/snapshot'
)

blueprints = Blueprint(
    'v_snapshots',
    __name__,
    url_prefix='/snapshots'
)


def show():
    url = url_for('api_snapshots.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in request.args.items():
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render_template('snapshots_show.html', paging=ret['data']['paging'],
                           page=ret['data']['page'], page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                           pages=ret['data']['pages'], order_by=ret['data']['order_by'], order=ret['data']['order'],
                           last_page=ret['data']['last_page'], snapshots=ret['data']['snapshots'],
                           guests_mapping_by_uuid=ret['data']['guests_mapping_by_uuid'])


