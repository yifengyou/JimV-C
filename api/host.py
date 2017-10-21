#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request
import jimit as ji

from models import Database as db
from models import Utils, Rules, Host
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


@Utils.dumps2response
def r_get(nodes_id):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: nodes_id})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        if -1 == nodes_id.find(','):
            node_id = nodes_id
            if db.r.hexists(app.config['hosts_info'], node_id):
                v = json.loads(db.r.hget(app.config['hosts_info'], node_id))
                v = Host.alive_check(v)
                v['node_id'] = node_id
                ret['data'] = v

        else:
            for node_id in nodes_id.split(','):
                if db.r.hexists(app.config['hosts_info'], node_id):
                    v = json.loads(db.r.hget(app.config['hosts_info'], node_id))
                    v = Host.alive_check(v)
                    v['node_id'] = node_id
                    ret['data'].append(v)

            if ret['data'].__len__() > 1:
                ret['data'].sort(key=lambda _k: _k['boot_time'])

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
            v = Host.alive_check(v)
            v['node_id'] = k
            ret['data'].append(v)

        if ret['data'].__len__() > 1:
            ret['data'].sort(key=lambda _k: _k['boot_time'])

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
                v = Host.alive_check(v)
                v['node_id'] = k
                ret['data'].append(v)

        if ret['data'].__len__() > 1:
            ret['data'].sort(key=lambda _k: _k['boot_time'])

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

