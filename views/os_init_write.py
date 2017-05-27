#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from models import OSInit
from models import OSInitWrite
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2017/3/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'os_init_write',
    __name__,
    url_prefix='/api/os_init_write'
)

blueprints = Blueprint(
    'os_init_writes',
    __name__,
    url_prefix='/api/os_init_writes'
)


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

        if os_init_write.exist_by('path'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_init_write.path])
            return ret

        os_init_write.create()
        os_init_write.get_by('path')
        ret['data'] = os_init_write.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_init_write = OSInitWrite()

    args_rules = [
        Rules.ID.value
    ]

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
def r_delete(_id):
    os_init_write = OSInitWrite()

    args_rules = [
        Rules.ID.value
    ]
    os_init_write.id = _id

    try:
        ji.Check.previewing(args_rules, os_init_write.__dict__)

        if os_init_write.exist():
            os_init_write.delete()
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

        ret['data'], ret['paging']['total'] = OSInitWrite.get_by_filter(offset=offset, limit=limit, order_by=order_by,
                                                                        order=order, filter_str=filter_str)

        host_url = request.host_url.rstrip('/')
        other_str = '&filter=' + filter_str + '&order=' + order + '&order_by=' + order_by
        last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

        if page <= 1:
            ret['paging']['prev'] = host_url + blueprints.url_prefix + '?page=1&page_size=' + page_size.__str__() + \
                                    other_str
        else:
            ret['paging']['prev'] = host_url + blueprints.url_prefix + '?page=' + str(page-1) + '&page_size=' + \
                                    page_size.__str__() + other_str

        if page >= last_pagination:
            ret['paging']['next'] = host_url + blueprints.url_prefix + '?page=' + last_pagination.__str__() + \
                                    '&page_size=' + page_size.__str__() + other_str
        else:
            ret['paging']['next'] = host_url + blueprints.url_prefix + '?page=' + str(page+1) + '&page_size=' + \
                                    page_size.__str__() + other_str

        ret['paging']['first'] = host_url + blueprints.url_prefix + '?page=1&page_size=' + \
            page_size.__str__() + other_str
        ret['paging']['last'] = \
            host_url + blueprints.url_prefix + '?page=' + last_pagination.__str__() + '&page_size=' + \
            page_size.__str__() + other_str

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)

