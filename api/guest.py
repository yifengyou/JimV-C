#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
from flask import Blueprint, url_for
from flask import request
import json
from uuid import uuid4
import jimit as ji

from api.base import Base
from models import DiskState, Host
from models.initialize import app, dev_table
from models import Database as db
from models import Config
from models import Disk
from models import Rules
from models import Utils
from models import Guest
from models import OSTemplateImage
from models import OSTemplateProfile
from models import OSTemplateInitializeOperate
from models import GuestXML
from models import SSHKeyGuestMapping
from models import SSHKey
from models import Snapshot
from models import status


__author__ = 'James Iter'
__date__ = '2017/3/22'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_guest',
    __name__,
    url_prefix='/api/guest'
)

blueprints = Blueprint(
    'api_guests',
    __name__,
    url_prefix='/api/guests'
)


guest_base = Base(the_class=Guest, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.CPU.value,
        Rules.MEMORY.value,
        Rules.BANDWIDTH.value,
        Rules.BANDWIDTH_UNIT.value,
        Rules.OS_TEMPLATE_IMAGE_ID.value,
        Rules.QUANTITY.value,
        Rules.REMARK.value,
        Rules.PASSWORD.value,
        Rules.LEASE_TERM.value
    ]

    if 'node_id' in request.json:
        args_rules.append(
            Rules.NODE_ID.value
        )

    if 'ssh_keys_id' in request.json:
        args_rules.append(
            Rules.SSH_KEYS_ID.value
        )

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ji.Check.previewing(args_rules, request.json)

        config = Config()
        config.id = 1
        config.get()

        os_template_image = OSTemplateImage()
        os_template_profile = OSTemplateProfile()

        os_template_image.id = request.json.get('os_template_image_id')
        if not os_template_image.exist():
            ret['state'] = ji.Common.exchange_state(40450)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template_image.id.__str__()])
            return ret

        os_template_image.get()
        os_template_profile.id = os_template_image.os_template_profile_id
        os_template_profile.get()

        os_template_initialize_operates, os_template_initialize_operates_count = \
            OSTemplateInitializeOperate.get_by_filter(
                filter_str='os_template_initialize_operate_set_id:eq:' +
                           os_template_profile.os_template_initialize_operate_set_id.__str__())

        if db.r.scard(app.config['ip_available_set']) < 1:
            ret['state'] = ji.Common.exchange_state(50350)
            return ret

        node_id = request.json.get('node_id', None)

        # 默认只取可随机分配虚拟机的 hosts
        available_hosts = Host.get_available_hosts(nonrandom=False)

        # 当指定了 host 时，取全部活着的 hosts
        if node_id is not None:
            available_hosts = Host.get_available_hosts(nonrandom=None)

        if available_hosts.__len__() == 0:
            ret['state'] = ji.Common.exchange_state(50351)
            return ret

        if node_id is not None and node_id not in [host['node_id'] for host in available_hosts]:
            ret['state'] = ji.Common.exchange_state(50351)
            return ret

        ssh_keys_id = request.json.get('ssh_keys_id', list())
        ssh_keys = list()
        ssh_key_guest_mapping = SSHKeyGuestMapping()

        if ssh_keys_id.__len__() > 0:
            rows, _ = SSHKey.get_by_filter(
                filter_str=':'.join(['id', 'in', ','.join(_id.__str__() for _id in ssh_keys_id)]))

            for row in rows:
                ssh_keys.append(row['public_key'])

        bandwidth = request.json.get('bandwidth')
        bandwidth_unit = request.json.get('bandwidth_unit')

        if bandwidth_unit == 'k':
            bandwidth = bandwidth * 1000

        elif bandwidth_unit == 'm':
            bandwidth = bandwidth * 1000 ** 2

        elif bandwidth_unit == 'g':
            bandwidth = bandwidth * 1000 ** 3

        else:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(41203)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        quantity = request.json.get('quantity')

        while quantity:
            quantity -= 1
            guest = Guest()
            guest.uuid = uuid4().__str__()
            guest.cpu = request.json.get('cpu')
            # 虚拟机内存单位，模板生成方法中已置其为GiB
            guest.memory = request.json.get('memory')
            guest.bandwidth = bandwidth
            guest.os_template_image_id = request.json.get('os_template_image_id')
            guest.label = ji.Common.generate_random_code(length=8)
            guest.remark = request.json.get('remark', '')

            guest.password = request.json.get('password')
            if guest.password is None or guest.password.__len__() < 1:
                guest.password = ji.Common.generate_random_code(length=16)

            guest.ip = db.r.spop(app.config['ip_available_set'])
            db.r.sadd(app.config['ip_used_set'], guest.ip)

            guest.network = config.vm_network
            guest.manage_network = config.vm_manage_network

            guest.vnc_port = db.r.spop(app.config['vnc_port_available_set'])
            db.r.sadd(app.config['vnc_port_used_set'], guest.vnc_port)

            guest.vnc_password = ji.Common.generate_random_code(length=16)

            disk = Disk()
            disk.uuid = guest.uuid
            disk.remark = guest.label.__str__() + '_SystemImage'
            disk.format = 'qcow2'
            disk.sequence = 0
            disk.size = 0
            disk.path = config.storage_path + '/' + disk.uuid + '.' + disk.format
            disk.guest_uuid = ''
            # disk.node_id 由 guest 事件处理机更新。涉及迁移时，其所属 node_id 会变更。参见 @models/event_processory.py:111 附近。
            disk.node_id = 0
            disk.quota(config=config)
            disk.create()

            guest_xml = GuestXML(guest=guest, disk=disk, config=config, os_type=os_template_profile.os_type)
            guest.xml = guest_xml.get_domain()

            # 在可用计算节点中平均分配任务
            chosen_host = available_hosts[quantity % available_hosts.__len__()]
            guest.node_id = chosen_host['node_id']

            if node_id is not None:
                guest.node_id = node_id

            guest.node_id = int(guest.node_id)
            guest.create()

            ssh_key_guest_mapping.guest_uuid = guest.uuid

            if ssh_keys_id.__len__() > 0:
                for ssh_key_id in ssh_keys_id:
                    ssh_key_guest_mapping.ssh_key_id = ssh_key_id
                    ssh_key_guest_mapping.create()

            # 替换占位符为有效内容
            _os_template_initialize_operates = copy.deepcopy(os_template_initialize_operates)
            for k, v in enumerate(_os_template_initialize_operates):
                _os_template_initialize_operates[k]['content'] = v['content'].replace('{IP}', guest.ip).\
                    replace('{HOSTNAME}', guest.label). \
                    replace('{PASSWORD}', guest.password). \
                    replace('{NETMASK}', config.netmask).\
                    replace('{GATEWAY}', config.gateway).\
                    replace('{DNS1}', config.dns1).\
                    replace('{DNS2}', config.dns2). \
                    replace('{SSH-KEY}', '\n'.join(ssh_keys))

                _os_template_initialize_operates[k]['command'] = v['command'].replace('{IP}', guest.ip). \
                    replace('{HOSTNAME}', guest.label). \
                    replace('{PASSWORD}', guest.password). \
                    replace('{NETMASK}', config.netmask). \
                    replace('{GATEWAY}', config.gateway). \
                    replace('{DNS1}', config.dns1). \
                    replace('{DNS2}', config.dns2). \
                    replace('{SSH-KEY}', '\n'.join(ssh_keys))

            message = {
                '_object': 'guest',
                'action': 'create',
                'uuid': guest.uuid,
                'storage_mode': config.storage_mode,
                'dfs_volume': config.dfs_volume,
                'node_id': guest.node_id,
                'name': guest.label,
                'template_path': os_template_image.path,
                'os_type': os_template_profile.os_type,
                'disks': [disk.__dict__],
                'xml': guest_xml.get_domain(),
                'os_template_initialize_operates': _os_template_initialize_operates,
                'passback_parameters': {}
            }

            Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_reboot(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'reboot',
                'uuid': uuid,
                'node_id': guest.node_id
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_force_reboot(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')
            disks, _ = Disk.get_by_filter(filter_str=':'.join(['guest_uuid', 'eq', guest.uuid]))

            message = {
                '_object': 'guest',
                'action': 'force_reboot',
                'uuid': uuid,
                'node_id': guest.node_id,
                'disks': disks
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_shutdown(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'shutdown',
                'uuid': uuid,
                'node_id': guest.node_id
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_force_shutdown(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'force_shutdown',
                'uuid': uuid,
                'node_id': guest.node_id
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_boot(uuids):
    # TODO: 做好关系依赖判断，比如boot不可以对suspend的实例操作。

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        config = Config()
        config.id = 1
        config.get()

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            disks, _ = Disk.get_by_filter(filter_str=':'.join(['guest_uuid', 'eq', guest.uuid]))

            message = {
                '_object': 'guest',
                'action': 'boot',
                'uuid': uuid,
                'node_id': guest.node_id,
                'passback_parameters': {},
                'disks': disks
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_suspend(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'suspend',
                'uuid': uuid,
                'node_id': guest.node_id
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_resume(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'resume',
                'uuid': uuid,
                'node_id': guest.node_id
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(uuids):

    args_rules = [
        Rules.UUIDS.value
    ]

    # TODO: 加入是否删除使用的数据磁盘开关，如果为True，则顺便删除使用的磁盘。否则解除该磁盘被使用的状态。
    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        # 检测所指定的 UUDIs 实例都存在
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        config = Config()
        config.id = 1
        config.get()

        # 执行删除操作
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'delete',
                'uuid': uuid,
                'storage_mode': config.storage_mode,
                'dfs_volume': config.dfs_volume,
                'node_id': guest.node_id
            }

            Utils.emit_instruction(message=json.dumps(message))

            # 删除创建失败的 Guest
            if guest.status == status.GuestState.dirty.value:
                disk = Disk()
                disk.uuid = guest.uuid
                disk.get_by('uuid')

                if disk.state == status.DiskState.pending.value:
                    disk.delete()
                    guest.delete()
                    SSHKeyGuestMapping.delete_by_filter(filter_str=':'.join(['guest_uuid', 'eq', guest.uuid]))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_attach_disk(uuid, disk_uuid):

    args_rules = [
        Rules.UUID.value,
        Rules.DISK_UUID.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid, 'disk_uuid': disk_uuid})

        guest = Guest()
        guest.uuid = uuid
        guest.get_by('uuid')

        disk = Disk()
        disk.uuid = disk_uuid
        disk.get_by('uuid')

        config = Config()
        config.id = 1
        config.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        # 判断欲挂载的磁盘是否空闲
        if disk.guest_uuid.__len__() > 0 or disk.state != DiskState.idle.value:
            ret['state'] = ji.Common.exchange_state(41258)
            return ret

        # 判断 Guest 是否处于可用状态
        if guest.status in (status.GuestState.no_state.value, status.GuestState.dirty.value):
            ret['state'] = ji.Common.exchange_state(41259)
            return ret

        # 判断 Guest 与 磁盘是否在同一宿主机上
        if config.storage_mode in [status.StorageMode.local.value, status.StorageMode.shared_mount.value]:
            if guest.node_id != disk.node_id:
                ret['state'] = ji.Common.exchange_state(41260)
                return ret

        # 通过检测未被使用的序列，来确定当前磁盘在目标 Guest 身上的序列
        disk.guest_uuid = guest.uuid
        disks, count = disk.get_by_filter(filter_str='guest_uuid:in:' + guest.uuid)

        already_used_sequence = list()

        for _disk in disks:
            already_used_sequence.append(_disk['sequence'])

        for sequence in range(0, dev_table.__len__()):
            if sequence not in already_used_sequence:
                disk.sequence = sequence
                break

        disk.state = DiskState.mounting.value

        guest_xml = GuestXML(guest=guest, disk=disk, config=config)

        message = {
            '_object': 'guest',
            'action': 'attach_disk',
            'uuid': uuid,
            'node_id': guest.node_id,
            'xml': guest_xml.get_disk(),
            'passback_parameters': {'disk_uuid': disk.uuid, 'sequence': disk.sequence},
            'disks': [disk.__dict__]
        }

        Utils.emit_instruction(message=json.dumps(message))
        disk.update()

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_detach_disk(disk_uuid):

    args_rules = [
        Rules.DISK_UUID.value
    ]

    try:
        ji.Check.previewing(args_rules, {'disk_uuid': disk_uuid})

        disk = Disk()
        disk.uuid = disk_uuid
        disk.get_by('uuid')

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if disk.state != DiskState.mounted.value or disk.sequence == 0:
            # 表示未被任何实例使用，已被分离
            # 序列为 0 的表示实例系统盘，系统盘不可以被分离
            # TODO: 系统盘单独范围其它状态
            return ret

        guest = Guest()
        guest.uuid = disk.guest_uuid
        guest.get_by('uuid')

        # 判断 Guest 是否处于可用状态
        if guest.status in (status.GuestState.no_state.value, status.GuestState.dirty.value):
            ret['state'] = ji.Common.exchange_state(41259)
            return ret

        config = Config()
        config.id = 1
        config.get()

        guest_xml = GuestXML(guest=guest, disk=disk, config=config)

        message = {
            '_object': 'guest',
            'action': 'detach_disk',
            'uuid': disk.guest_uuid,
            'node_id': guest.node_id,
            'xml': guest_xml.get_disk(),
            'passback_parameters': {'disk_uuid': disk.uuid}
        }

        Utils.emit_instruction(message=json.dumps(message))

        disk.state = DiskState.unloading.value
        disk.update()

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_migrate(uuids, destination_host):

    args_rules = [
        Rules.UUIDS.value,
        Rules.DESTINATION_HOST.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids, 'destination_host': destination_host})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        config = Config()
        config.id = 1
        config.get()

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            message = {
                '_object': 'guest',
                'action': 'migrate',
                'uuid': uuid,
                'node_id': guest.node_id,
                'storage_mode': config.storage_mode,
                'duri': 'qemu+ssh://' + destination_host + '/system'
            }

            Utils.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(uuids):
    ret = guest_base.get(ids=uuids, ids_rule=Rules.UUIDS.value, by_field='uuid')

    if '200' != ret['state']['code']:
        return ret

    rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['guest_uuid', 'in', uuids]))

    guest_uuid_ssh_key_id_mapping = dict()
    ssh_keys_id = list()

    for row in rows:
        if row['ssh_key_id'] not in ssh_keys_id:
            ssh_keys_id.append(row['ssh_key_id'].__str__())

        if row['guest_uuid'] not in guest_uuid_ssh_key_id_mapping:
            guest_uuid_ssh_key_id_mapping[row['guest_uuid']] = list()

        guest_uuid_ssh_key_id_mapping[row['guest_uuid']].append(row['ssh_key_id'])

    rows, _ = SSHKey.get_by_filter(filter_str=':'.join(['id', 'in', ','.join(ssh_keys_id)]))

    ssh_key_id_mapping = dict()

    for row in rows:
        row['url'] = url_for('v_ssh_keys.show')
        ssh_key_id_mapping[row['id']] = row

    if -1 == uuids.find(','):
        if 'ssh_keys' not in ret['data']:
            ret['data']['ssh_keys'] = list()

        if ret['data']['uuid'] in guest_uuid_ssh_key_id_mapping:
            for ssh_key_id in guest_uuid_ssh_key_id_mapping[ret['data']['uuid']]:

                if ssh_key_id not in ssh_key_id_mapping:
                    continue

                ret['data']['ssh_keys'].append(ssh_key_id_mapping[ssh_key_id])

    else:
        for i, guest in enumerate(ret['data']):
            if 'ssh_keys' not in ret['data'][i]:
                ret['data'][i]['ssh_keys'] = list()

            if ret['data'][i]['uuid'] in guest_uuid_ssh_key_id_mapping:
                for ssh_key_id in guest_uuid_ssh_key_id_mapping[ret['data'][i]['uuid']]:

                    if ssh_key_id not in ssh_key_id_mapping:
                        continue

                    ret['data'][i]['ssh_keys'].append(ssh_key_id_mapping[ssh_key_id])

    return ret


@Utils.dumps2response
def r_get_by_filter():
    ret = guest_base.get_by_filter()

    uuids = list()
    for guest in ret['data']:
        uuids.append(guest['uuid'])

    rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['guest_uuid', 'in', ','.join(uuids)]))

    guest_uuid_ssh_key_id_mapping = dict()
    ssh_keys_id = list()

    for row in rows:
        if row['ssh_key_id'] not in ssh_keys_id:
            ssh_keys_id.append(row['ssh_key_id'].__str__())

        if row['guest_uuid'] not in guest_uuid_ssh_key_id_mapping:
            guest_uuid_ssh_key_id_mapping[row['guest_uuid']] = list()

        guest_uuid_ssh_key_id_mapping[row['guest_uuid']].append(row['ssh_key_id'])

    rows, _ = SSHKey.get_by_filter(filter_str=':'.join(['id', 'in', ','.join(ssh_keys_id)]))

    ssh_key_id_mapping = dict()

    for row in rows:
        row['url'] = url_for('v_ssh_keys.show')
        ssh_key_id_mapping[row['id']] = row

    rows, _ = Snapshot.get_by_filter(filter_str=':'.join(['guest_uuid', 'in', ','.join(uuids)]))

    snapshots_guest_uuid_mapping = dict()

    for row in rows:
        guest_uuid = row['guest_uuid']
        if guest_uuid not in snapshots_guest_uuid_mapping:
            snapshots_guest_uuid_mapping[guest_uuid] = list()

        snapshots_guest_uuid_mapping[guest_uuid].append(row)

    for i, guest in enumerate(ret['data']):

        guest_uuid = ret['data'][i]['uuid']

        if 'ssh_keys' not in ret['data'][i]:
            ret['data'][i]['ssh_keys'] = list()

        if guest_uuid in guest_uuid_ssh_key_id_mapping:
            for ssh_key_id in guest_uuid_ssh_key_id_mapping[guest_uuid]:

                if ssh_key_id not in ssh_key_id_mapping:
                    continue

                ret['data'][i]['ssh_keys'].append(ssh_key_id_mapping[ssh_key_id])

        if 'snapshot' not in ret['data'][i]:
            ret['data'][i]['snapshot'] = {
                'creatable': True,
                'mapping': list()
            }

        if guest_uuid in snapshots_guest_uuid_mapping:
            ret['data'][i]['snapshot']['mapping'] = snapshots_guest_uuid_mapping[guest_uuid]

            for snapshot in snapshots_guest_uuid_mapping[guest_uuid]:
                if snapshot['progress'] == 100:
                    continue

                else:
                    ret['data'][i]['snapshot']['creatable'] = False

    return ret


@Utils.dumps2response
def r_content_search():
    ret = guest_base.content_search()

    uuids = list()
    for guest in ret['data']:
        uuids.append(guest['uuid'])

    rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['guest_uuid', 'in', ','.join(uuids)]))

    guest_uuid_ssh_key_id_mapping = dict()
    ssh_keys_id = list()

    for row in rows:
        if row['ssh_key_id'] not in ssh_keys_id:
            ssh_keys_id.append(row['ssh_key_id'].__str__())

        if row['guest_uuid'] not in guest_uuid_ssh_key_id_mapping:
            guest_uuid_ssh_key_id_mapping[row['guest_uuid']] = list()

        guest_uuid_ssh_key_id_mapping[row['guest_uuid']].append(row['ssh_key_id'])

    rows, _ = SSHKey.get_by_filter(filter_str=':'.join(['id', 'in', ','.join(ssh_keys_id)]))

    ssh_key_id_mapping = dict()

    for row in rows:
        row['url'] = url_for('v_ssh_keys.show')
        ssh_key_id_mapping[row['id']] = row

    rows, _ = Snapshot.get_by_filter(filter_str=':'.join(['guest_uuid', 'in', ','.join(uuids)]))

    snapshots_guest_uuid_mapping = dict()

    for row in rows:
        guest_uuid = row['guest_uuid']
        if guest_uuid not in snapshots_guest_uuid_mapping:
            snapshots_guest_uuid_mapping[guest_uuid] = list()

        snapshots_guest_uuid_mapping[guest_uuid].append(row)

    for i, guest in enumerate(ret['data']):

        guest_uuid = ret['data'][i]['uuid']

        if 'ssh_keys' not in ret['data'][i]:
            ret['data'][i]['ssh_keys'] = list()

        if guest_uuid in guest_uuid_ssh_key_id_mapping:
            for ssh_key_id in guest_uuid_ssh_key_id_mapping[guest_uuid]:

                if ssh_key_id not in ssh_key_id_mapping:
                    continue

                ret['data'][i]['ssh_keys'].append(ssh_key_id_mapping[ssh_key_id])

        if 'snapshot' not in ret['data'][i]:
            ret['data'][i]['snapshot'] = {
                'creatable': True,
                'mapping': list()
            }

        if guest_uuid in snapshots_guest_uuid_mapping:
            ret['data'][i]['snapshot']['mapping'] = snapshots_guest_uuid_mapping[guest_uuid]

            for snapshot in snapshots_guest_uuid_mapping[guest_uuid]:
                if snapshot['progress'] == 100:
                    continue

                else:
                    ret['data'][i]['snapshot']['creatable'] = False

    return ret


@Utils.dumps2response
def r_distribute_count():
    from models import Guest
    rows, count = Guest.get_all()

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'os_template_image_id': dict(),
        'status': dict(),
        'node_id': dict(),
        'cpu_memory': dict(),
        'cpu': 0,
        'memory': 0,
        'guests': rows.__len__()
    }

    for guest in rows:
        if guest['os_template_image_id'] not in ret['data']['os_template_image_id']:
            ret['data']['os_template_image_id'][guest['os_template_image_id']] = 0

        if guest['status'] not in ret['data']['status']:
            ret['data']['status'][guest['status']] = 0

        if guest['node_id'] not in ret['data']['node_id']:
            ret['data']['node_id'][guest['node_id']] = 0

        cpu_memory = '_'.join([str(guest['cpu']), str(guest['memory'])])
        if cpu_memory not in ret['data']['cpu_memory']:
            ret['data']['cpu_memory'][cpu_memory] = 0

        ret['data']['os_template_image_id'][guest['os_template_image_id']] += 1
        ret['data']['status'][guest['status']] += 1
        ret['data']['node_id'][guest['node_id']] += 1
        ret['data']['cpu_memory'][cpu_memory] += 1

        ret['data']['cpu'] += guest['cpu']
        ret['data']['memory'] += guest['memory']

    return ret


@Utils.dumps2response
def r_update(uuid):

    args_rules = [
        Rules.UUID.value
    ]

    if 'remark' in request.json:
        args_rules.append(
            Rules.REMARK.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['uuid'] = uuid

    try:
        ji.Check.previewing(args_rules, request.json)
        guest = Guest()
        guest.uuid = uuid
        guest.get_by('uuid')

        guest.remark = request.json.get('remark', guest.label)

        guest.update()
        guest.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = guest.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_reset_password(uuids, password):

    args_rules = [
        Rules.UUIDS.value,
        Rules.PASSWORD.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids, 'password': password})

        guest = Guest()
        os_template_image = OSTemplateImage()
        os_template_profile = OSTemplateProfile()

        # 检测所指定的 UUDIs 实例都存在
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            os_template_image.id = guest.os_template_image_id
            os_template_image.get()

            os_template_profile.id = os_template_image.os_template_profile_id
            os_template_profile.get()

            user = 'root'

            if os_template_profile.os_type == 'windows':
                user = 'administrator'

            # guest.password 由 guest 事件处理机更新。参见 @models/event_processory.py:189 附近。

            message = {
                '_object': 'guest',
                'action': 'reset_password',
                'uuid': guest.uuid,
                'node_id': guest.node_id,
                'os_type': os_template_profile.os_type,
                'user': user,
                'password': password,
                'passback_parameters': {'password': password}
            }

            Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_allocate_bandwidth(uuids, bandwidth, bandwidth_unit):

    args_rules = [
        Rules.UUIDS.value,
        Rules.BANDWIDTH_IN_URL.value,
        Rules.BANDWIDTH_UNIT.value,
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids, 'bandwidth': bandwidth, 'bandwidth_unit': bandwidth_unit})

        bandwidth = int(bandwidth)

        if bandwidth_unit == 'k':
            bandwidth = bandwidth * 1000

        elif bandwidth_unit == 'm':
            bandwidth = bandwidth * 1000 ** 2

        elif bandwidth_unit == 'g':
            bandwidth = bandwidth * 1000 ** 3

        else:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(41203)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        guest = Guest()

        # 检测所指定的 UUDIs 实例都存在
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')
            guest.bandwidth = bandwidth

            message = {
                '_object': 'guest',
                'action': 'allocate_bandwidth',
                'uuid': guest.uuid,
                'node_id': guest.node_id,
                'bandwidth': guest.bandwidth,
                'passback_parameters': {'bandwidth': guest.bandwidth}
            }

            Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

