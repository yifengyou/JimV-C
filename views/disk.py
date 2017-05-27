#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, request
import json
from uuid import uuid4
import jimit as ji

from models import Guest, DiskState
from models.initialize import app, dev_table
from models import Database as db
from models import Config
from models import Disk
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2017/4/24'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'disk',
    __name__,
    url_prefix='/api/disk'
)

blueprints = Blueprint(
    'disks',
    __name__,
    url_prefix='/api/disks'
)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.DISK_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, request.json)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        size = request.json['size']

        if size < 1:
            ret['state'] = ji.Common.exchange_state(41255)
            return ret

        disk = Disk()
        disk.guest_uuid = ''
        disk.size = size
        disk.uuid = uuid4().__str__()
        disk.label = ji.Common.generate_random_code(length=8)
        disk.sequence = -1
        disk.format = 'qcow2'

        config = Config()
        config.id = 1
        config.get()

        disk.path = config.storage_path + '/' + disk.uuid + '.' + disk.format

        message = {'action': 'create_disk', 'glusterfs_volume': config.glusterfs_volume,
                   'image_path': disk.path, 'size': disk.size, 'uuid': disk.uuid}

        db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        disk.create()

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_resize(uuid, size):

    args_rules = [
        Rules.UUID.value,
        Rules.DISK_SIZE_STR.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid, 'size': size})

        disk = Disk()
        disk.uuid = uuid
        disk.get_by('uuid')

        used = True

        if disk.guest_uuid.__len__() != 36:
            used = False

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if disk.size >= size:
            ret['state'] = ji.Common.exchange_state(41257)
            return ret

        message = {'action': 'resize_disk', 'size': size, 'guest_uuid': disk.guest_uuid,
                   'disk_uuid': disk.uuid, 'passback_parameters': {'size': size}}

        if used:
            message['device_node'] = dev_table[disk.sequence]
            Guest.emit_instruction(message=json.dumps(message))
        else:
            config = Config()
            config.id = 1
            config.get()

            message['glusterfs_volume'] = config.glusterfs_volume
            message['image_path'] = disk.path

            db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        disk = Disk()

        # 检测所指定的 UUDIs 磁盘都存在
        for uuid in uuids.split(','):
            disk.uuid = uuid
            disk.get_by('uuid')

            if disk.state != DiskState.idle.value:
                ret['state'] = ji.Common.exchange_state(41256)
                return ret

        config = Config()
        config.id = 1
        config.get()

        # 执行删除操作
        for uuid in uuids.split(','):
            disk.uuid = uuid
            disk.get_by('uuid')

            message = {'action': 'delete_disk', 'uuid': disk.uuid,
                       'glusterfs_volume': config.glusterfs_volume, 'image_path': disk.path}
            db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(uuid):
    disk = Disk()

    args_rules = [
        Rules.UUID.value
    ]
    disk.uuid = uuid

    try:
        ji.Check.previewing(args_rules, disk.__dict__)
        disk.get_by('uuid')
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = disk.__dict__
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

        ret['data'], ret['paging']['total'] = Disk.get_by_filter(offset=offset, limit=limit, order_by=order_by,
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


@Utils.dumps2response
def r_content_search():
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
    keyword = request.args.get('keyword', '')

    args_rules = [
        Rules.OFFSET.value,
        Rules.LIMIT.value,
        Rules.ORDER_BY.value,
        Rules.ORDER.value,
        Rules.KEYWORD.value
    ]

    try:
        ji.Check.previewing(args_rules, {'offset': offset, 'limit': limit, 'order_by': order_by, 'order': order,
                                         'keyword': keyword})
        offset = int(offset)
        limit = int(limit)
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()
        ret['paging'] = {'total': 0, 'offset': offset, 'limit': limit, 'page': page, 'page_size': page_size}

        ret['data'], ret['paging']['total'] = Disk.content_search(offset=offset, limit=limit, order_by=order_by,
                                                                  order=order, keyword=keyword)

        host_url = request.host_url.rstrip('/')
        other_str = '&keyword=' + keyword + '&order=' + order + '&order_by=' + order_by
        last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

        if page <= 1:
            ret['paging']['prev'] = host_url + blueprints.url_prefix + '/_search?page=1&page_size=' + \
                                    page_size.__str__() + other_str
        else:
            ret['paging']['prev'] = host_url + blueprints.url_prefix + '/_search?page=' + str(page-1) + \
                                    '&page_size=' + page_size.__str__() + other_str

        if page >= last_pagination:
            ret['paging']['next'] = host_url + blueprints.url_prefix + '/_search?page=' + last_pagination.__str__() + \
                                    '&page_size=' + page_size.__str__() + other_str
        else:
            ret['paging']['next'] = host_url + blueprints.url_prefix + '/_search?page=' + str(page+1) + \
                                    '&page_size=' + page_size.__str__() + other_str

        ret['paging']['first'] = host_url + blueprints.url_prefix + '/_search?page=1&page_size=' + \
            page_size.__str__() + other_str
        ret['paging']['last'] = \
            host_url + blueprints.url_prefix + '/_search?page=' + last_pagination.__str__() + '&page_size=' + \
            page_size.__str__() + other_str

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(uuid):

    args_rules = [
        Rules.UUID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['uuid'] = uuid

    try:
        ji.Check.previewing(args_rules, request.json)
        disk = Disk()
        disk.uuid = uuid
        disk.get_by('uuid')

        disk.label = request.json.get('label', disk.label)

        disk.update()
        disk.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = disk.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)

