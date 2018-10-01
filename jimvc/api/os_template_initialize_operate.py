#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from jimvc.api.base import Base
from jimvc.models import Rules
from jimvc.models import Utils
from jimvc.models import OSTemplateInitializeOperate
from jimvc.models import OSTemplateInitializeOperateSet
from jimvc.models import OSTemplateInitializeOperateKind


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_os_template_initialize_operate',
    __name__,
    url_prefix='/api/os_template_initialize_operate'
)

blueprints = Blueprint(
    'api_os_template_initialize_operates',
    __name__,
    url_prefix='/api/os_template_initialize_operates'
)


os_template_initialize_operate_base = \
    Base(the_class=OSTemplateInitializeOperate, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_template_initialize_operate_set = OSTemplateInitializeOperateSet()
    os_template_initialize_operate = OSTemplateInitializeOperate()

    args_rules = [
        Rules.OS_TEMPLATE_INITIALIZE_OPERATE_SET_ID_EXT.value,
        Rules.OS_TEMPLATE_INITIALIZE_OPERATE_KIND.value,
        Rules.OS_TEMPLATE_INITIALIZE_OPERATE_SEQUENCE.value
    ]

    os_template_initialize_operate.os_template_initialize_operate_set_id = \
        request.json.get('os_template_initialize_operate_set_id')
    os_template_initialize_operate.kind = request.json.get('kind')
    os_template_initialize_operate.path = request.json.get('path', '')
    os_template_initialize_operate.sequence = request.json.get('sequence', 0)
    os_template_initialize_operate.content = request.json.get('content', '')
    os_template_initialize_operate.command = request.json.get('command', '')

    if os_template_initialize_operate.kind == OSTemplateInitializeOperateKind.cmd.value:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_COMMAND.value
        )

    else:
        args_rules.extend([
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_PATH.value,
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_CONTENT.value
        ])

    try:
        ji.Check.previewing(args_rules, os_template_initialize_operate.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        os_template_initialize_operate_set.id = os_template_initialize_operate.os_template_initialize_operate_set_id
        if not os_template_initialize_operate_set.exist():
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 操作系统初始化操作集ID: ',
                                                    os_template_initialize_operate_set.id.__str__()])
            return ret

        if os_template_initialize_operate.kind == OSTemplateInitializeOperateKind.cmd.value:
            data, total = os_template_initialize_operate.get_by_filter(
                filter_str=':'.join(['os_template_initialize_operate_set_id', 'eq',
                                     os_template_initialize_operate.os_template_initialize_operate_set_id.__str__()]) +
                           ';' + ':'.join(['command', 'eq', os_template_initialize_operate.command]))

        else:
            data, total = os_template_initialize_operate.get_by_filter(
                filter_str=':'.join(['os_template_initialize_operate_set_id', 'eq',
                                     os_template_initialize_operate.os_template_initialize_operate_set_id.__str__()]) +
                           ';' + ':'.join(['path', 'eq', os_template_initialize_operate.path]))

        if data.__len__() > 0:
            ret['state'] = ji.Common.exchange_state(40901)

            if os_template_initialize_operate.kind == OSTemplateInitializeOperateKind.cmd.value:
                ret['state']['sub']['zh-cn'] = ''.join(
                    [ret['state']['sub']['zh-cn'], u', 命令: ', os_template_initialize_operate.command,
                     u', 已存在于操作集ID ',
                     os_template_initialize_operate.os_template_initialize_operate_set_id.__str__(), u' 中。'])

            else:
                ret['state']['sub']['zh-cn'] = ''.join([
                    ret['state']['sub']['zh-cn'], u', 路径: ', os_template_initialize_operate.path,
                    u', 已存在于操作集ID ',
                    os_template_initialize_operate.os_template_initialize_operate_set_id.__str__(), u' 中。'])
            return ret

        os_template_initialize_operate.create()
        data, total = os_template_initialize_operate.get_by_filter(
            filter_str=':'.join(['os_template_initialize_operate_set_id', 'eq',
                                 os_template_initialize_operate.os_template_initialize_operate_set_id.__str__()]) + ';'
                       + ':'.join(['path', 'eq', os_template_initialize_operate.path]))
        ret['data'] = data[0]
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_template_initialize_operate = OSTemplateInitializeOperate()

    args_rules = [
        Rules.ID.value
    ]

    if 'os_template_initialize_operate_set_id' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_SET_ID_EXT.value,
        )

    if 'kind' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_KIND.value,
        )

    if 'sequence' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_SEQUENCE.value,
        )

    if 'path' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_PATH.value,
        )

    if 'content' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_CONTENT.value,
        )

    if 'command' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_COMMAND.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_template_initialize_operate.id = request.json.get('id')
        os_template_initialize_operate.get()
        os_template_initialize_operate.os_template_initialize_operate_set_id = \
            request.json.get('os_template_initialize_operate_set_id',
                             os_template_initialize_operate.os_template_initialize_operate_set_id)
        os_template_initialize_operate.kind = request.json.get('kind', os_template_initialize_operate.kind)
        os_template_initialize_operate.sequence = request.json.get('sequence', os_template_initialize_operate.sequence)
        os_template_initialize_operate.path = request.json.get('path', os_template_initialize_operate.path)
        os_template_initialize_operate.content = request.json.get('content', os_template_initialize_operate.content)
        os_template_initialize_operate.command = request.json.get('command', os_template_initialize_operate.command)

        os_template_initialize_operate.update()
        os_template_initialize_operate.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_template_initialize_operate.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    return os_template_initialize_operate_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_template_initialize_operate_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_template_initialize_operate_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_template_initialize_operate_base.content_search()
