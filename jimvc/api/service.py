#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji
import json
from flask import Blueprint
from flask import request

from jimvc.api.base import Base
from jimvc.models import Utils
from jimvc.models import Guest
from jimvc.models import Rules
from jimvc.models import Service


__author__ = 'James Iter'
__date__ = '2018/10/7'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_service',
    __name__,
    url_prefix='/api/service'
)

blueprints = Blueprint(
    'api_services',
    __name__,
    url_prefix='/api/services'
)


service_base = Base(the_class=Service, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.PROJECT_ID.value,
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

        service = Service()
        service.project_id = request.json.get('project_id', None)
        service.name = request.json.get('name', None)
        service.description = request.json.get('description', '')

        service.create()
        service.get_by('create_time')

        ret['data'] = service.__dict__
        return ret

    except ji.PreviewingError as e:
        return json.loads(str(e))


@Utils.dumps2response
def r_update(_id):

    service = Service()

    args_rules = [
        Rules.ID.value
    ]

    if 'project_id' in request.json:
        args_rules.append(
            Rules.PROJECT_ID.value,
        )

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
        service.id = int(request.json.get('id'))

        service.get()
        service.project_id = request.json.get('project_id', service.project_id)
        service.name = request.json.get('name', service.name)
        service.description = request.json.get('description', service.description)

        service.update()
        service.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = service.__dict__
        return ret
    except ji.PreviewingError as e:
        return json.loads(str(e))


@Utils.dumps2response
def r_get(ids):
    return service_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return service_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return service_base.content_search()


@Utils.dumps2response
def r_delete(ids):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'ids': ids})

        service = Service()

        # 检测所指定的 项目 都存在
        for _id in ids.split(','):
            service.id = int(_id)
            service.get()

        # 执行删除操作
        for _id in ids.split(','):
            if int(_id) == 1:
                # 默认服务组不允许被删除
                continue

            Guest.update_by_filter({'service_id': 1}, filter_str='service_id:eq:' + _id)
            service.id = int(_id)
            service.get()
            service.delete()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError as e:
        return json.loads(str(e))

