#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request, g
import jimit as ji
import json

from api.base import Base
from models import OSInit
from models import OSInitWrite
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2017/3/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'os_init',
    __name__,
    url_prefix='/api/os_init'
)

blueprints = Blueprint(
    'os_inits',
    __name__,
    url_prefix='/api/os_inits'
)


os_init_base = Base(the_class=OSInit, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_init = OSInit()

    args_rules = [
        Rules.NAME.value,
        Rules.REMARK.value
    ]

    os_init.name = request.json.get('name')
    os_init.remark = request.json.get('remark')

    try:
        ji.Check.previewing(args_rules, os_init.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if os_init.exist_by('name'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_init.name])
            return ret

        os_init.create()
        os_init.get_by('name')
        ret['data'] = os_init.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_init = OSInit()

    args_rules = [
        Rules.ID.value
    ]

    if 'name' in request.json:
        args_rules.append(
            Rules.NAME.value,
        )

    if 'remark' in request.json:
        args_rules.append(
            Rules.REMARK.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_init.id = request.json.get('id')
        os_init.get()
        os_init.name = request.json.get('name', os_init.name)
        os_init.remark = request.json.get('remark', os_init.remark)

        os_init.update()
        g.config = None

        os_init.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_init.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    os_init_write_base = Base(the_class=OSInitWrite)
    os_init_write_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='os_init_id')

    return os_init_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_init_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_init_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_init_base.content_search()

