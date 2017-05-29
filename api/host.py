#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request
import jimit as ji

from models import Database as db
from models import Utils, Rules
from models.initialize import app


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'host',
    __name__,
    url_prefix='/api/host'
)

blueprints = Blueprint(
    'hosts',
    __name__,
    url_prefix='/api/hosts'
)


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
                ret['data'] = {_id: json.loads(db.r.hget(app.config['hosts_info'], _id))}

        else:
            for _id in ids.split(','):
                if db.r.hexists(app.config['hosts_info'], _id):
                    ret['data'].append({_id: json.loads(db.r.hget(app.config['hosts_info'], _id))})

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
            ret['data'].append({k: json.loads(v)})

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
                ret['data'].append({k: v})

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

