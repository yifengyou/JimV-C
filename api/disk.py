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

from base import Base


__author__ = 'James Iter'
__date__ = '2017/4/24'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_disk',
    __name__,
    url_prefix='/api/disk'
)

blueprints = Blueprint(
    'api_disks',
    __name__,
    url_prefix='/api/disks'
)


disk_base = Base(the_class=Disk, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.DISK_SIZE.value,
        Rules.REMARK.value,
        Rules.QUANTITY.value
    ]

    try:
        ji.Check.previewing(args_rules, request.json)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        size = request.json['size']
        quantity = request.json.get('quantity')

        if size < 1:
            ret['state'] = ji.Common.exchange_state(41255)
            return ret

        while quantity:
            quantity -= 1
            disk = Disk()
            disk.guest_uuid = ''
            disk.size = size
            disk.uuid = uuid4().__str__()
            disk.remark = request.json.get('remark', '')
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

        message = {'action': 'resize_disk', 'size': int(size), 'guest_uuid': disk.guest_uuid,
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
def r_get(uuids):
    return disk_base.get(ids=uuids, ids_rule=Rules.UUIDS.value, by_field='uuid')


@Utils.dumps2response
def r_get_by_filter():
    return disk_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return disk_base.content_search()


@Utils.dumps2response
def r_update(uuid):

    args_rules = [
        Rules.UUID.value
    ]

    if 'remark' in request.json:
        args_rules.append(
            Rules.REMARK.value
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

        disk.remark = request.json.get('remark', disk.remark)

        disk.update()
        disk.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = disk.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_distribute_count():
    from models import Disk
    rows, count = Disk.get_all()

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'kind': {'system': 0, 'data_mounted': 0, 'data_idle': 0},
        'total_size': 0,
        'disks': rows.__len__()
    }

    for disk in rows:
        if disk['sequence'] == 0:
            ret['data']['kind']['system'] += 1

        elif disk['sequence'] < 0:
            ret['data']['kind']['data_idle'] += 1

        else:
            ret['data']['kind']['data_mounted'] += 1

        ret['data']['total_size'] += disk['size']

    return ret


