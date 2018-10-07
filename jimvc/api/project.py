#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji
import json
from flask import Blueprint
from flask import request

from jimvc.api.base import Base
from jimvc.models import Utils
from jimvc.models import Rules
from jimvc.models import Project


__author__ = 'James Iter'
__date__ = '2018/10/7'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_project',
    __name__,
    url_prefix='/api/project'
)

blueprints = Blueprint(
    'api_projects',
    __name__,
    url_prefix='/api/projects'
)


project_base = Base(the_class=Project, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.NAME.value
    ]

    if 'description' in request.json:
        args_rules.append(
            Rules.DESCRIPTION.value,
        )

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ji.Check.previewing(args_rules, request.json)

        project = Project()
        project.name = request.json.get('name', None)
        project.description = request.json.get('description', '')

        project.create()
        project.get_by('create_time')

        ret['data'] = project.__dict__
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    project = Project()

    args_rules = [
        Rules.ID.value
    ]

    if 'name' in request.json:
        args_rules.append(
            Rules.NAME.value,
        )

    if 'description' in request.json:
        args_rules.append(
            Rules.DESCRIPTION.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        project.id = int(request.json.get('id'))

        project.get()
        project.name = request.json.get('name', project.name)
        project.description = request.json.get('description', project.description)

        project.update()
        project.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = project.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(ids):
    return project_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return project_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return project_base.content_search()


@Utils.dumps2response
def r_delete(ids):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'ids': ids})

        project = Project()

        # 检测所指定的 项目 都存在
        for _id in ids.split(','):
            project.id = int(_id)
            project.get()

        # 执行删除操作
        for _id in ids.split(','):
            project.id = int(_id)
            project.get()
            project.delete()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

