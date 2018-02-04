#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request, g
import jimit as ji
import json

from api.base import Base
from models import Rules
from models import Utils
from models import OSTemplateInitializeOperateSet, OSTemplateInitializeOperate


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_os_template_initialize_operate_set',
    __name__,
    url_prefix='/api/os_template_initialize_operate_set'
)

blueprints = Blueprint(
    'api_os_templates_initialize_operate_set',
    __name__,
    url_prefix='/api/os_templates_initialize_operate_set'
)


os_template_initialize_operate_set_base = Base(the_class=OSTemplateInitializeOperateSet,
                                               the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_template_initialize_operate_set = OSTemplateInitializeOperateSet()

    args_rules = [
        Rules.LABEL.value,
        Rules.DESCRIBE.value,
        Rules.ACTIVE.value
    ]

    os_template_initialize_operate_set.label = request.json.get('label')
    os_template_initialize_operate_set.describe = request.json.get('describe')
    os_template_initialize_operate_set.active = request.json.get('active')

    try:
        ji.Check.previewing(args_rules, os_template_initialize_operate_set.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if os_template_initialize_operate_set.exist_by('label'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ',
                                                    os_template_initialize_operate_set.label])
            return ret

        os_template_initialize_operate_set.create()
        os_template_initialize_operate_set.get_by('label')
        ret['data'] = os_template_initialize_operate_set.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_template_initialize_operate_set = OSTemplateInitializeOperateSet()

    args_rules = [
        Rules.ID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if 'describe' in request.json:
        args_rules.append(
            Rules.DESCRIBE.value,
        )

    if 'active' in request.json:
        args_rules.append(
            Rules.ACTIVE.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_template_initialize_operate_set.id = request.json.get('id')
        os_template_initialize_operate_set.get()
        os_template_initialize_operate_set.label = request.json.get('label', os_template_initialize_operate_set.label)
        os_template_initialize_operate_set.describe = \
            request.json.get('describe', os_template_initialize_operate_set.describe)
        os_template_initialize_operate_set.active = \
            request.json.get('active', os_template_initialize_operate_set.active)

        os_template_initialize_operate_set.update()
        os_template_initialize_operate_set.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_template_initialize_operate_set.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    os_template_initialize_operate_base = Base(the_class=OSTemplateInitializeOperate)
    os_template_initialize_operate_base.delete(ids=ids, ids_rule=Rules.IDS.value,
                                               by_field='os_template_initialize_operate_set_id')

    return os_template_initialize_operate_set_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_template_initialize_operate_set_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_template_initialize_operate_set_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_template_initialize_operate_set_base.content_search()

