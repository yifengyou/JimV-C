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
from jimvc.models import Service


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
    ret = project_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')

    project_ids = list()

    if -1 == ids.find(','):
        project_ids.append(ret['data']['id'])

    else:
        for project in ret['data']:
            project_ids.append(project['id'])

    rows, _ = Service.get_by_filter(filter_str=':'.join([
        'project_id', 'in', ','.join(project_id.__str__() for project_id in project_ids)]))

    services_mapping_by_project_id = dict()

    for row in rows:
        if row['project_id'] not in services_mapping_by_project_id:
            services_mapping_by_project_id[row['project_id']] = list()

        services_mapping_by_project_id[row['project_id']].append(row)

    if -1 == ids.find(','):
        ret['data']['services'] = services_mapping_by_project_id[ret['data']['id']]

    else:
        for i, project in enumerate(ret['data']):
            ret['data'][i]['services'] = services_mapping_by_project_id[project['id']]

    return ret


@Utils.dumps2response
def r_get_by_filter():
    ret = project_base.get_by_filter()

    project_ids = list()
    for project in ret['data']:
        project_ids.append(project['id'])

    rows, _ = Service.get_by_filter(filter_str=':'.join([
        'project_id', 'in', ','.join(project_id.__str__() for project_id in project_ids)]))

    services_mapping_by_project_id = dict()

    for row in rows:
        if row['project_id'] not in services_mapping_by_project_id:
            services_mapping_by_project_id[row['project_id']] = list()

        services_mapping_by_project_id[row['project_id']].append(row)

    for i, project in enumerate(ret['data']):
        ret['data'][i]['services'] = services_mapping_by_project_id[project['id']]

    return ret


@Utils.dumps2response
def r_content_search():
    ret = project_base.content_search()

    project_ids = list()
    for project in ret['data']:
        project_ids.append(project['id'])

    rows, _ = Service.get_by_filter(filter_str=':'.join([
        'project_id', 'in', ','.join(project_id.__str__() for project_id in project_ids)]))

    services_mapping_by_project_id = dict()

    for row in rows:
        if row['project_id'] not in services_mapping_by_project_id:
            services_mapping_by_project_id[row['project_id']] = list()

        services_mapping_by_project_id[row['project_id']].append(row)

    for i, project in enumerate(ret['data']):
        ret['data'][i]['services'] = services_mapping_by_project_id[project['id']]

    return ret


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

