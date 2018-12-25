#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, request
import json
import jimit as ji

from jimvc.models import Utils
from jimvc.models import Rules
from jimvc.models import ReservedIP

from base import Base


__author__ = 'James Iter'
__date__ = '2018-12-25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_reserved_ip',
    __name__,
    url_prefix='/api/reserved_ip'
)

blueprints = Blueprint(
    'api_reserved_ips',
    __name__,
    url_prefix='/api/reserved_ips'
)


reserved_ip_base = Base(the_class=ReservedIP, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.IP.value
    ]

    reserved_ip = ReservedIP()
    reserved_ip.ip = request.json.get('ip', '')

    try:
        ji.Check.previewing(args_rules, reserved_ip.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        reserved_ip.create()

        reserved_ip.get()
        ret['data'] = reserved_ip.__dict__

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(ids):
    return reserved_ip_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return reserved_ip_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return reserved_ip_base.content_search()


@Utils.dumps2response
def r_delete(ids):
    return reserved_ip_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')

