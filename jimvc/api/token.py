#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json

from flask import Blueprint
import jimit as ji
import time

from jimvc.models import Utils, Rules
from jimvc.models import Token


__author__ = 'James Iter'
__date__ = '2019-01-01'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2019 by James Iter.'


blueprint = Blueprint(
    'api_token',
    __name__,
    url_prefix='/api/token'
)

blueprints = Blueprint(
    'api_tokens',
    __name__,
    url_prefix='/api/tokens'
)


@Utils.dumps2response
def r_create():

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        token = Token()
        token.generator()
        token.create()

        ret['data'] = {
            'token': token.token,
            'ttl': token.ttl,
            'expire': time.strftime('%Y-%m-%dT%H:%M:%S %Z', time.localtime(ji.Common.ts() + token.ttl))
        }

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get_by_filter():

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        ts = ji.Common.ts()

        for token in Token.get_all():
            expire = time.strftime('%Y-%m-%dT%H:%M:%S %Z', time.localtime(token[1]))
            ret['data'].append({'token': token[0], 'expire': expire, 'ttl': token[1] - ts})

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(tokens):

    args_rules = [
        Rules.TOKENS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: tokens})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        token = Token()

        for _token in tokens.split(','):
            token.token = _token
            if token.delete():
                ret['data'].append(_token)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


