#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, request
import json
from uuid import uuid4
import jimit as ji

from models import Guest, DiskState
from models.initialize import dev_table
from models import Config
from models import Disk
from models import Rules
from models import Utils
from models.status import StorageMode

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
        Rules.DISK_ON_HOST.value,
        Rules.QUANTITY.value
    ]

    config = Config()
    config.id = 1
    config.get()

    if config.storage_mode in [StorageMode.shared_mount.value, StorageMode.ceph.value,
                               StorageMode.glusterfs.value]:
        request.json['on_host'] = 'shared_storage'

    try:
        ji.Check.previewing(args_rules, request.json)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        size = request.json['size']
        quantity = request.json['quantity']
        on_host = request.json['on_host']

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
            disk.on_host = on_host
            disk.sequence = -1
            disk.format = 'qcow2'
            disk.path = config.storage_path + '/' + disk.uuid + '.' + disk.format
            disk.quota(config=config)

            message = {
                '_object': 'disk',
                'action': 'create',
                'uuid': disk.uuid,
                'storage_mode': config.storage_mode,
                'dfs_volume': config.dfs_volume,
                'hostname': disk.on_host,
                'image_path': disk.path,
                'size': disk.size
            }

            if disk.on_host == 'shared_storage':
                available_hosts = Guest.get_available_hosts()

                if available_hosts.__len__() == 0:
                    ret['state'] = ji.Common.exchange_state(50351)
                    return ret

                # 在可用计算节点中平均分配任务
                chosen_host = available_hosts[quantity % available_hosts.__len__()]
                message['hostname'] = chosen_host['hostname']

            Guest.emit_instruction(message=json.dumps(message, ensure_ascii=False))

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

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if disk.size >= int(size):
            ret['state'] = ji.Common.exchange_state(41257)
            return ret

        config = Config()
        config.id = 1
        config.get()

        disk.size = int(size)
        disk.quota(config=config)
        # 将在事件返回层(models/event_processor.py:224 附近)，更新数据库中 disk 对象

        message = {
            '_object': 'disk',
            'action': 'resize',
            'uuid': disk.uuid,
            'guest_uuid': disk.guest_uuid,
            'storage_mode': config.storage_mode,
            'size': disk.size,
            'dfs_volume': config.dfs_volume,
            'hostname': disk.on_host,
            'image_path': disk.path,
            'disks': [disk.__dict__],
            'passback_parameters': {'size': disk.size}
        }

        if disk.on_host == 'shared_storage':
            message['hostname'] = Guest.get_lightest_host()['hostname']

        if disk.guest_uuid.__len__() == 36:
            message['device_node'] = dev_table[disk.sequence]

        Guest.emit_instruction(message=json.dumps(message, ensure_ascii=False))

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

            message = {
                '_object': 'disk',
                'action': 'delete',
                'uuid': disk.uuid,
                'storage_mode': config.storage_mode,
                'dfs_volume': config.dfs_volume,
                'hostname': disk.on_host,
                'image_path': disk.path
            }

            if disk.on_host == 'shared_storage':
                message['hostname'] = Guest.get_lightest_host()['hostname']

            Guest.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


def add_device(func):
    from functools import wraps

    @wraps(func)
    def _add_device(*args, **kwargs):
        ret = func(*args, **kwargs)
        if ret['data'].__len__() > 0:
            if isinstance(ret['data'], list):
                for i, item in enumerate(ret['data']):
                    ret['data'][i][u'device'] = u'/dev/' + dev_table[item['sequence']]

            elif isinstance(ret['data'], dict):
                ret['data'][u'device'] = u'/dev/' + dev_table[ret['data']['sequence']]

            else:
                raise json.dumps(ret)

        return ret

    return _add_device


@Utils.dumps2response
@add_device
def r_get(uuids):
    return disk_base.get(ids=uuids, ids_rule=Rules.UUIDS.value, by_field='uuid')


@Utils.dumps2response
@add_device
def r_get_by_filter():
    return disk_base.get_by_filter()


@Utils.dumps2response
@add_device
def r_content_search():
    return disk_base.content_search()


@Utils.dumps2response
def r_update(uuids):

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = list()

    args_rules = [
        Rules.UUIDS.value
    ]

    if 'remark' in request.json:
        args_rules.append(
            Rules.REMARK.value
        )

    if 'iops' in request.json:
        args_rules.append(
            Rules.IOPS.value
        )

    if 'iops_rd' in request.json:
        args_rules.append(
            Rules.IOPS_RD.value
        )

    if 'iops_wr' in request.json:
        args_rules.append(
            Rules.IOPS_WR.value
        )

    if 'iops_max' in request.json:
        args_rules.append(
            Rules.IOPS_MAX.value
        )

    if 'iops_max_length' in request.json:
        args_rules.append(
            Rules.IOPS_MAX_LENGTH.value
        )

    if 'bps' in request.json:
        args_rules.append(
            Rules.BPS.value
        )

    if 'bps_rd' in request.json:
        args_rules.append(
            Rules.BPS_RD.value
        )

    if 'bps_wr' in request.json:
        args_rules.append(
            Rules.BPS_WR.value
        )

    if 'bps_max' in request.json:
        args_rules.append(
            Rules.BPS_MAX.value
        )

    if 'bps_max_length' in request.json:
        args_rules.append(
            Rules.BPS_MAX_LENGTH.value
        )

    if args_rules.__len__() < 2:
        return ret

    request.json['uuids'] = uuids

    need_update_quota = False
    need_update_quota_parameters = ['iops', 'iops_rd', 'iops_wr', 'iops_max', 'iops_max_length',
                                    'bps', 'bps_rd', 'bps_wr', 'bps_max', 'bps_max_length']

    if filter(lambda p: p in request.json, need_update_quota_parameters).__len__() > 0:
        need_update_quota = True

    try:
        ji.Check.previewing(args_rules, request.json)

        disk = Disk()

        # 检测所指定的 UUDIs 磁盘都存在
        for uuid in uuids.split(','):
            disk.uuid = uuid
            disk.get_by('uuid')

        for uuid in uuids.split(','):
            disk.uuid = uuid
            disk.get_by('uuid')
            disk.remark = request.json.get('remark', disk.remark)
            disk.iops = request.json.get('iops', disk.iops)
            disk.iops_rd = request.json.get('iops_rd', disk.iops_rd)
            disk.iops_wr = request.json.get('iops_wr', disk.iops_wr)
            disk.iops_max = request.json.get('iops_max', disk.iops_max)
            disk.iops_max_length = request.json.get('iops_max_length', disk.iops_max_length)
            disk.bps = request.json.get('bps', disk.bps)
            disk.bps_rd = request.json.get('bps_rd', disk.bps_rd)
            disk.bps_wr = request.json.get('bps_wr', disk.bps_wr)
            disk.bps_max = request.json.get('bps_max', disk.bps_max)
            disk.bps_max_length = request.json.get('bps_max_length', disk.bps_max_length)
            disk.update()
            disk.get()

            if disk.sequence >= 0 and need_update_quota:
                message = {
                    '_object': 'disk',
                    'action': 'quota',
                    'uuid': disk.uuid,
                    'guest_uuid': disk.guest_uuid,
                    'hostname': disk.on_host,
                    'disks': [disk.__dict__]
                }

                Guest.emit_instruction(message=json.dumps(message))

            ret['data'].append(disk.__dict__)

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


