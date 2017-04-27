#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, request
import json
from uuid import uuid4
import jimit as ji

from models import Guest
from models.initialize import app, dev_table
from models import Database as db
from models import Config
from models import GuestDisk
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

        guest_disk = GuestDisk()
        guest_disk.guest_uuid = ''
        guest_disk.size = size
        guest_disk.uuid = uuid4().__str__()
        guest_disk.label = ji.Common.generate_random_code(length=8)
        guest_disk.sequence = -1
        guest_disk.format = 'qcow2'

        config = Config()
        config.id = 1
        config.get()

        image_path = '/'.join(['DiskPool', guest_disk.uuid + '.' + guest_disk.format])

        message = {'action': 'create_disk', 'glusterfs_volume': config.glusterfs_volume,
                   'image_path': image_path, 'size': guest_disk.size}

        db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        guest_disk.create()

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_resize(uuid, size):

    args_rules = [
        Rules.UUID.value,
        Rules.DISK_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid, 'size': size})

        guest_disk = GuestDisk()
        guest_disk.uuid = uuid
        guest_disk.get_by('uuid')

        used = True

        if guest_disk.guest_uuid.__len__() != 36:
            used = False

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if guest_disk.size <= size:
            ret['state'] = ji.Common.exchange_state(41257)
            return ret

        guest_disk.size = size
        guest_disk.update()

        message = {'action': 'resize_disk', 'size': size}

        if used:
            message['uuid'] = guest_disk.guest_uuid
            message['device_node'] = dev_table[guest_disk.sequence]
            Guest.emit_instruction(message=json.dumps(message))
        else:
            config = Config()
            config.id = 1
            config.get()

            image_path = '/'.join(['DiskPool', guest_disk.uuid + '.' + guest_disk.format])
            message['glusterfs_volume'] = config.glusterfs_volume
            message['image_path'] = image_path

            db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(uuid):

    args_rules = [
        Rules.UUID.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid})

        guest_disk = GuestDisk()
        guest_disk.uuid = uuid
        guest_disk.get_by('uuid')

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if guest_disk.guest_uuid.__len__() > 0:
            ret['state'] = ji.Common.exchange_state(41256)
            return ret

        config = Config()
        config.id = 1
        config.get()

        image_path = '/'.join(['DiskPool', guest_disk.uuid + '.' + guest_disk.format])

        message = {'action': 'delete_disk', 'glusterfs_volume': config.glusterfs_volume, 'image_path': image_path}
        db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        guest_disk.delete()

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)
