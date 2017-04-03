#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

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


@Utils.dumps2response
def r_create():

    os_template = OSTemplate()

    args_rules = [
        Rules.LABEL.value,
        Rules.NAME.value,
        Rules.ACTIVE.value,
        Rules.OS_INIT_ID_EXT.value
    ]

    os_template.label = request.json.get('label')
    os_template.name = request.json.get('name')
    os_template.active = request.json.get('active')
    os_template.os_init_id = request.json.get('os_init_id', 0)

    try:
        ji.Check.previewing(args_rules, os_template.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if os_template.exist_by('name'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template.name])
            return ret

        os_template.create()
        os_template.get_by('name')
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

    if 'name' in request.json:
        args_rules.append(
            Rules.NAME.value,
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
        os_template.name = request.json.get('name', os_template.name)
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
def r_delete(_id):
    os_template = OSTemplate()

    args_rules = [
        Rules.ID.value
    ]
    os_template.id = _id

    try:
        ji.Check.previewing(args_rules, os_template.__dict__)

        if os_template.exist():
            os_template.delete()
        else:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40401)
            return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get_by_filter():
    page = str(request.args.get('page', 1))
    page_size = str(request.args.get('page_size', 50))

    args_rules = [
        Rules.PAGE.value,
        Rules.PAGE_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'page': page, 'page_size': page_size})
    except ji.PreviewingError, e:
        return json.loads(e.message)

    page = int(page)
    page_size = int(page_size)

    # 把page和page_size换算成offset和limit
    offset = (page - 1) * page_size
    # offset, limit将覆盖page及page_size的影响
    offset = str(request.args.get('offset', offset))
    limit = str(request.args.get('limit', page_size))

    order_by = request.args.get('order_by', 'id')
    order = request.args.get('order', 'asc')
    filter_str = request.args.get('filter', '')

    args_rules = [
        Rules.OFFSET.value,
        Rules.LIMIT.value,
        Rules.ORDER_BY.value,
        Rules.ORDER.value
    ]

    try:
        ji.Check.previewing(args_rules, {'offset': offset, 'limit': limit, 'order_by': order_by, 'order': order})
        offset = int(offset)
        limit = int(limit)
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()
        ret['paging'] = {'total': 0, 'offset': offset, 'limit': limit, 'page': page, 'page_size': page_size,
                         'next': '', 'prev': '', 'first': '', 'last': ''}

        ret['data'], ret['paging']['total'] = OSTemplate.get_by_filter(offset=offset, limit=limit, order_by=order_by,
                                                                       order=order, filter_str=filter_str)

        host_url = request.host_url.rstrip('/')
        other_str = '&filter=' + filter_str + '&order=' + order + '&order_by=' + order_by
        last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

        if page <= 1:
            ret['paging']['prev'] = host_url + blueprint.url_prefix + '?page=1&page_size=' + page_size.__str__() + \
                                    other_str
        else:
            ret['paging']['prev'] = host_url + blueprint.url_prefix + '?page=' + str(page-1) + '&page_size=' + \
                                    page_size.__str__() + other_str

        if page >= last_pagination:
            ret['paging']['next'] = host_url + blueprint.url_prefix + '?page=' + last_pagination.__str__() + \
                                    '&page_size=' + page_size.__str__() + other_str
        else:
            ret['paging']['next'] = host_url + blueprint.url_prefix + '?page=' + str(page+1) + '&page_size=' + \
                                    page_size.__str__() + other_str

        ret['paging']['first'] = host_url + blueprint.url_prefix + '?page=1&page_size=' + \
            page_size.__str__() + other_str
        ret['paging']['last'] = \
            host_url + blueprint.url_prefix + '?page=' + last_pagination.__str__() + '&page_size=' + \
            page_size.__str__() + other_str

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)
