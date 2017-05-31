#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
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
    'api_os_init_write',
    __name__,
    url_prefix='/api/os_init_write'
)

blueprints = Blueprint(
    'api_os_init_writes',
    __name__,
    url_prefix='/api/os_init_writes'
)


os_init_write_base = Base(the_class=OSInitWrite, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_init = OSInit()
    os_init_write = OSInitWrite()

    args_rules = [
        Rules.OS_INIT_ID_EXT.value,
        Rules.OS_INIT_WRITE_PATH.value,
        Rules.OS_INIT_WRITE_CONTENT.value
    ]

    os_init_write.os_init_id = request.json.get('os_init_id')
    os_init_write.path = request.json.get('path')
    os_init_write.content = request.json.get('content')

    try:
        ji.Check.previewing(args_rules, os_init_write.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        os_init.id = os_init_write.os_init_id
        if not os_init.exist():
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_init.id.__str__()])
            return ret

        data, total = os_init_write.get_by_filter(
            filter_str=':'.join(['os_init_id','eq',os_init_write.os_init_id.__str__()]) + ';' +
                       ':'.join(['path', 'eq', os_init_write.path]))

        if data.__len__() > 0:
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ', path: ', os_init_write.path,
                                                    ', os_init_id: ', os_init_write.os_init_id.__str__()])
            return ret

        os_init_write.create()
        data, total = os_init_write.get_by_filter(
            filter_str=':'.join(['os_init_id','eq',os_init_write.os_init_id.__str__()]) + ';' +
                       ':'.join(['path', 'eq', os_init_write.path]))
        ret['data'] = data[0]
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_init_write = OSInitWrite()

    args_rules = [
        Rules.ID.value
    ]

    if 'os_init_id' in request.json:
        args_rules.append(
            Rules.OS_INIT_ID_EXT.value,
        )

    if 'path' in request.json:
        args_rules.append(
            Rules.OS_INIT_WRITE_PATH.value,
        )

    if 'content' in request.json:
        args_rules.append(
            Rules.OS_INIT_WRITE_CONTENT.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_init_write.id = request.json.get('id')
        os_init_write.get()
        os_init_write.os_init_id = request.json.get('os_init_id', os_init_write.os_init_id)
        os_init_write.path = request.json.get('path', os_init_write.path)
        os_init_write.content = request.json.get('content', os_init_write.content)

        os_init_write.update()
        os_init_write.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_init_write.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    return os_init_write_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_init_write_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_init_write_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_init_write_base.content_search()

