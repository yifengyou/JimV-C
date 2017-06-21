#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from api.base import Base
from models import Rules
from models import Utils
from models.boot_job import OperateRule, BootJob
from models.status import OperateRuleKind

__author__ = 'James Iter'
__date__ = '2017/6/19'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_operate_rule',
    __name__,
    url_prefix='/api/operate_rule'
)

blueprints = Blueprint(
    'api_operate_rules',
    __name__,
    url_prefix='/api/operate_rules'
)


operate_rule_base = Base(the_class=OperateRule, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    boot_job = BootJob()
    operate_rule = OperateRule()

    args_rules = [
        Rules.BOOT_JOB_ID_EXT.value,
        Rules.OPERATE_RULE_KIND.value,
        Rules.OPERATE_RULE_SEQUENCE.value
    ]

    operate_rule.boot_job_id = request.json.get('boot_job_id')
    operate_rule.kind = request.json.get('kind')
    operate_rule.path = request.json.get('path', '')
    operate_rule.sequence = request.json.get('sequence', 0)
    operate_rule.content = request.json.get('content', '')
    operate_rule.command = request.json.get('command', '')

    if operate_rule.kind == OperateRuleKind.cmd.value:
        args_rules.append(
            Rules.OPERATE_RULE_COMMAND.value
        )

    else:
        args_rules.extend([
            Rules.OPERATE_RULE_PATH.value,
            Rules.OPERATE_RULE_CONTENT.value
        ])

    try:
        ji.Check.previewing(args_rules, operate_rule.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        boot_job.id = operate_rule.boot_job_id
        if not boot_job.exist():
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', boot_job.id.__str__()])
            return ret

        if operate_rule.kind == OperateRuleKind.cmd.value:
            data, total = operate_rule.get_by_filter(
                filter_str=':'.join(['boot_job_id', 'eq', operate_rule.boot_job_id.__str__()]) + ';' +
                           ':'.join(['command', 'eq', operate_rule.command]))

        else:
            data, total = operate_rule.get_by_filter(
                filter_str=':'.join(['boot_job_id', 'eq', operate_rule.boot_job_id.__str__()]) + ';' +
                           ':'.join(['path', 'eq', operate_rule.path]))

        if data.__len__() > 0:
            ret['state'] = ji.Common.exchange_state(40901)

            if operate_rule.kind == OperateRuleKind.cmd.value:
                ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'],
                                                        ', command: ', operate_rule.command,
                                                        ', boot_job_id: ', operate_rule.boot_job_id.__str__()])

            else:
                ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ', path: ', operate_rule.path,
                                                        ', boot_job_id: ', operate_rule.boot_job_id.__str__()])
            return ret

        operate_rule.create()
        data, total = operate_rule.get_by_filter(
            filter_str=':'.join(['boot_job_id', 'eq', operate_rule.boot_job_id.__str__()]) + ';' +
                       ':'.join(['path', 'eq', operate_rule.path]))
        ret['data'] = data[0]
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    operate_rule = OperateRule()

    args_rules = [
        Rules.ID.value
    ]

    if 'boot_job_id' in request.json:
        args_rules.append(
            Rules.BOOT_JOB_ID_EXT.value,
        )

    if 'kind' in request.json:
        args_rules.append(
            Rules.OPERATE_RULE_KIND.value,
        )

    if 'sequence' in request.json:
        args_rules.append(
            Rules.OPERATE_RULE_SEQUENCE.value,
        )

    if 'path' in request.json:
        args_rules.append(
            Rules.OPERATE_RULE_PATH.value,
        )

    if 'content' in request.json:
        args_rules.append(
            Rules.OPERATE_RULE_CONTENT.value,
        )

    if 'command' in request.json:
        args_rules.append(
            Rules.OPERATE_RULE_COMMAND.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        operate_rule.id = request.json.get('id')
        operate_rule.get()
        operate_rule.boot_job_id = request.json.get('boot_job_id', operate_rule.boot_job_id)
        operate_rule.kind = request.json.get('kind', operate_rule.kind)
        operate_rule.sequence = request.json.get('sequence', operate_rule.sequence)
        operate_rule.path = request.json.get('path', operate_rule.path)
        operate_rule.content = request.json.get('content', operate_rule.content)
        operate_rule.command = request.json.get('command', operate_rule.command)

        operate_rule.update()
        operate_rule.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = operate_rule.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    return operate_rule_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return operate_rule_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return operate_rule_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return operate_rule_base.content_search()

