#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from jimvc.models import Config, Disk
from jimvc.models import Rules
from jimvc.models import Utils


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_config',
    __name__,
    url_prefix='/api/config'
)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.JIMV_EDITION.value,
        Rules.STORAGE_MODE.value,
        Rules.DFS_VOLUME.value,
        Rules.STORAGE_PATH.value,
        Rules.VM_NETWORK.value,
        Rules.VM_MANAGE_NETWORK.value,
        Rules.IOPS_BASE.value,
        Rules.IOPS_PRE_UNIT.value,
        Rules.IOPS_CAP.value,
        Rules.IOPS_MAX.value,
        Rules.IOPS_MAX_LENGTH.value,
        Rules.BPS_BASE.value,
        Rules.BPS_PRE_UNIT.value,
        Rules.BPS_CAP.value,
        Rules.BPS_MAX.value,
        Rules.BPS_MAX_LENGTH.value
    ]

    config = Config()
    config.id = 1
    config.jimv_edition = int(request.json.get('jimv_edition', 0))
    config.storage_mode = int(request.json.get('storage_mode', 0))
    config.dfs_volume = request.json.get('dfs_volume', '')
    config.storage_path = request.json.get('storage_path')
    config.vm_network = request.json.get('vm_network')
    config.vm_manage_network = request.json.get('vm_manage_network')
    config.iops_base = int(request.json.get('iops_base', 1000))
    config.iops_pre_unit = int(request.json.get('iops_pre_unit', 1))
    config.iops_cap = int(request.json.get('iops_cap', 2000))
    config.iops_max = int(request.json.get('iops_max', 3000))
    config.iops_max_length = int(request.json.get('iops_max_length', 20))
    # 200 MiB
    config.bps_base = int(request.json.get('bps_base', 1024 * 1024 * 200))
    # 0.3 MiB
    config.bps_pre_unit = int(request.json.get('bps_pre_unit', 1024 * 1024 * 0.3))
    # 500 MiB
    config.bps_cap = int(request.json.get('bps_cap', 1024 * 1024 * 500))
    # 1 GiB
    config.bps_max = int(request.json.get('bps_max', 1024 * 1024 * 1024))
    config.bps_max_length = int(request.json.get('bps_max_length', 10))

    try:
        ji.Check.previewing(args_rules, config.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if config.exist():
            ret['state'] = ji.Common.exchange_state(40901)
            return ret

        config.create()
        config.update_global_config()

        config.id = 1
        config.get()
        ret['data'] = config.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update():

    config = Config()

    args_rules = [
    ]

    if 'jimv_edition' in request.json:
        args_rules.append(
            Rules.JIMV_EDITION.value,
        )

    if 'storage_mode' in request.json:
        args_rules.append(
            Rules.STORAGE_MODE.value,
        )

    if 'dfs_volume' in request.json:
        args_rules.append(
            Rules.DFS_VOLUME.value,
        )

    if 'storage_path' in request.json:
        args_rules.append(
            Rules.STORAGE_PATH.value,
        )

    if 'vm_network' in request.json:
        args_rules.append(
            Rules.VM_NETWORK.value,
        )

    if 'vm_manage_network' in request.json:
        args_rules.append(
            Rules.VM_MANAGE_NETWORK.value,
        )

    if args_rules.__len__() < 1:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    try:
        config.id = 1
        ji.Check.previewing(args_rules, request.json)
        config.get()

        config.jimv_edition = int(request.json.get('jimv_edition', config.jimv_edition))
        config.storage_mode = int(request.json.get('storage_mode', config.storage_mode))
        config.dfs_volume = request.json.get('dfs_volume', config.dfs_volume)
        config.storage_path = request.json.get('storage_path', config.storage_path)
        config.vm_network = request.json.get('vm_network', config.vm_network)
        config.vm_manage_network = request.json.get('vm_manage_network', config.vm_manage_network)

        config.update()
        config.update_global_config()

        config.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = config.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update_quota():

    config = Config()

    args_rules = [
    ]

    if 'iops_base' in request.json:
        args_rules.append(
            Rules.IOPS_BASE.value,
        )

    if 'iops_pre_unit' in request.json:
        args_rules.append(
            Rules.IOPS_PRE_UNIT.value,
        )

    if 'iops_cap' in request.json:
        args_rules.append(
            Rules.IOPS_CAP.value,
        )

    if 'iops_max' in request.json:
        args_rules.append(
            Rules.IOPS_MAX.value,
        )

    if 'iops_max_length' in request.json:
        args_rules.append(
            Rules.IOPS_MAX_LENGTH.value,
        )

    if 'bps_base' in request.json:
        args_rules.append(
            Rules.BPS_BASE.value,
        )

    if 'bps_pre_unit' in request.json:
        args_rules.append(
            Rules.BPS_PRE_UNIT.value,
        )

    if 'bps_cap' in request.json:
        args_rules.append(
            Rules.BPS_CAP.value,
        )

    if 'bps_max' in request.json:
        args_rules.append(
            Rules.BPS_MAX.value,
        )

    if 'bps_max_length' in request.json:
        args_rules.append(
            Rules.BPS_MAX_LENGTH.value,
        )

    if 'influence_current_guest' in request.json:
        args_rules.append(
            Rules.INFLUENCE_CURRENT_GUEST.value,
        )

    if args_rules.__len__() < 1:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    try:
        config.id = 1
        ji.Check.previewing(args_rules, request.json)
        config.get()

        config.iops_base = int(request.json.get('iops_base', config.iops_base))
        config.iops_pre_unit = int(request.json.get('iops_pre_unit', config.iops_pre_unit))
        config.iops_cap = int(request.json.get('iops_cap', config.iops_cap))
        config.iops_max = int(request.json.get('iops_max', config.iops_max))
        config.iops_max_length = int(request.json.get('iops_max_length', config.iops_max_length))
        config.bps_base = int(request.json.get('bps_base', config.bps_base))
        config.bps_pre_unit = int(request.json.get('bps_pre_unit', config.bps_pre_unit))
        config.bps_cap = int(request.json.get('bps_cap', config.bps_cap))
        config.bps_max = int(request.json.get('bps_max', config.bps_max))
        config.bps_max_length = int(request.json.get('bps_max_length', config.bps_max_length))

        if request.json.get('influence_current_guest', False):
            disks, _ = Disk.get_all()

            disk = Disk()
            for disk_info in disks:
                disk.id = disk_info['id']
                disk.get()
                disk.quota(config=config)
                disk.update()

                if disk.sequence >= 0:
                    message = {
                        '_object': 'disk',
                        'action': 'quota',
                        'uuid': disk.uuid,
                        'guest_uuid': disk.guest_uuid,
                        'node_id': disk.node_id,
                        'disks': [disk.__dict__]
                    }

                    Utils.emit_instruction(message=json.dumps(message))

        config.update()
        config.update_global_config()

        config.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = config.__dict__

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get():

    config = Config()

    try:
        config.id = 1
        config.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = config.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)

