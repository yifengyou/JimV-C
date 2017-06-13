#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request, g
import jimit as ji

from models import Database as db
from models import Utils, Rules
from models.initialize import app


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_host',
    __name__,
    url_prefix='/api/host'
)

blueprints = Blueprint(
    'api_hosts',
    __name__,
    url_prefix='/api/hosts'
)


def alive_check(v):
    """
    JimV-C 2 秒更新一次宿主机信息，这里以 5 秒内没收到更新，作为判断宿主机是否在线的标准
    """

    if 'timestamp' not in v:
        return v

    v['alive'] = False
    if v['timestamp'] + 5 >= g.ts:
        v['alive'] = True

    return v


@Utils.dumps2response
def r_get(ids):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: ids})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        if -1 == ids.find(','):
            _id = ids
            if db.r.hexists(app.config['hosts_info'], _id):
                v = json.loads(db.r.hget(app.config['hosts_info'], _id))
                v = alive_check(v)
                v['uuid'] = _id
                ret['data'] = v

        else:
            for _id in ids.split(','):
                if db.r.hexists(app.config['hosts_info'], _id):
                    v = json.loads(db.r.hget(app.config['hosts_info'], _id))
                    v = alive_check(v)
                    v['uuid'] = _id
                    ret['data'].append(v)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get_by_filter():

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()
        for k, v in db.r.hgetall(app.config['hosts_info']).items():
            v = json.loads(v)
            v = alive_check(v)
            v['uuid'] = k
            ret['data'].append(v)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_content_search():
    keyword = request.args.get('keyword', '')

    args_rules = [
        Rules.KEYWORD.value
    ]

    try:
        ji.Check.previewing(args_rules, {'keyword': keyword})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        for k, v in db.r.hgetall(app.config['hosts_info']).items():
            v = json.loads(v)
            if -1 != v['hostname'].find(keyword):
                v = alive_check(v)
                v['uuid'] = k
                ret['data'].append(v)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

