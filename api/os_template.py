#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from api.base import Base
from models import OSTemplate
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2017/3/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'os_template',
    __name__,
    url_prefix='/api/os_template'
)

blueprints = Blueprint(
    'os_templates',
    __name__,
    url_prefix='/api/os_templates'
)


os_template_base = Base(the_class=OSTemplate, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_template = OSTemplate()

    args_rules = [
        Rules.LABEL.value,
        Rules.PATH.value,
        Rules.ACTIVE.value,
        Rules.OS_INIT_ID_EXT.value
    ]

    os_template.label = request.json.get('label')
    os_template.path = request.json.get('path')
    os_template.active = request.json.get('active')
    os_template.os_init_id = request.json.get('os_init_id', 0)

    try:
        ji.Check.previewing(args_rules, os_template.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if os_template.exist_by('path'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template.path])
            return ret

        os_template.create()
        os_template.get_by('path')
        ret['data'] = os_template.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_template = OSTemplate()

    args_rules = [
        Rules.ID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if 'path' in request.json:
        args_rules.append(
            Rules.PATH.value,
        )

    if 'active' in request.json:
        args_rules.append(
            Rules.ACTIVE.value,
        )

    if 'os_init_id' in request.json:
        args_rules.append(
            Rules.OS_INIT_ID_EXT.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_template.id = request.json.get('id')

        os_template.get()
        os_template.label = request.json.get('label', os_template.label)
        os_template.path = request.json.get('path', os_template.path)
        os_template.active = request.json.get('active', os_template.active)
        os_template.os_init_id = request.json.get('os_init_id', os_template.os_init_id)

        os_template.update()
        os_template.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_template.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    return os_template_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_template_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_template_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_template_base.content_search()

