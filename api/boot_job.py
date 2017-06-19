#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request, g
import jimit as ji
import json

from api.base import Base
from models import Rules
from models import Utils
from models.boot_job import BootJob, OperateRule


__author__ = 'James Iter'
__date__ = '2017/6/19'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_boot_job',
    __name__,
    url_prefix='/api/boot_job'
)

blueprints = Blueprint(
    'api_boot_jobs',
    __name__,
    url_prefix='/api/boot_jobs'
)


boot_job_base = Base(the_class=BootJob, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    boot_job = BootJob()

    args_rules = [
        Rules.NAME.value,
        Rules.USE_FOR.value,
        Rules.REMARK.value
    ]

    boot_job.name = request.json.get('name')
    boot_job.use_for = request.json.get('use_for')
    boot_job.remark = request.json.get('remark')

    try:
        ji.Check.previewing(args_rules, boot_job.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if boot_job.exist_by('name'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', boot_job.name])
            return ret

        boot_job.create()
        boot_job.get_by('name')
        ret['data'] = boot_job.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    boot_job = BootJob()

    args_rules = [
        Rules.ID.value
    ]

    if 'name' in request.json:
        args_rules.append(
            Rules.NAME.value,
        )

    if 'use_for' in request.json:
        args_rules.append(
            Rules.USE_FOR.value,
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
        boot_job.id = request.json.get('id')
        boot_job.get()
        boot_job.name = request.json.get('name', boot_job.name)
        boot_job.use_for = request.json.get('use_for', boot_job.use_for)
        boot_job.remark = request.json.get('remark', boot_job.remark)

        boot_job.update()
        g.config = None

        boot_job.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = boot_job.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    operate_rule_base = Base(the_class=OperateRule)
    operate_rule_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='boot_job_id')

    return boot_job_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return boot_job_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return boot_job_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return boot_job_base.content_search()

