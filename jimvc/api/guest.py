#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
from math import ceil
from IPy import IP

import requests
import json
from uuid import uuid4
import random
import time
import jimit as ji
from flask import Blueprint, url_for, request

from jimvc.api.base import Base
from jimvc.models.initialize import dev_table
from jimvc.models import app_config, GuestState, Service
from jimvc.models import DiskState, Host
from jimvc.models import Database as db
from jimvc.models import Config
from jimvc.models import Disk
from jimvc.models import Rules
from jimvc.models import Utils
from jimvc.models import Guest
from jimvc.models import OSTemplateImage
from jimvc.models import OSTemplateProfile
from jimvc.models import OSTemplateInitializeOperate
from jimvc.models import GuestXML
from jimvc.models import SSHKeyGuestMapping
from jimvc.models import SSHKey
from jimvc.models import Snapshot
from jimvc.models import status


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
os_template_image_base = Base(the_class=OSTemplateImage, the_blueprint=blueprint, the_blueprints=blueprints)
os_template_profile_base = Base(the_class=OSTemplateProfile, the_blueprint=blueprint, the_blueprints=blueprints)


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

    if 'service_id' in request.json:
        args_rules.append(
            Rules.SERVICE_ID.value
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

        if db.r.scard(app_config['ip_available_set']) < 1:
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

        available_hosts_mapping_by_node_id = dict()

        for host in available_hosts:
            if host['node_id'] not in available_hosts_mapping_by_node_id:
                available_hosts_mapping_by_node_id[host['node_id']] = host

        if node_id is not None and node_id not in available_hosts_mapping_by_node_id:
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

        # 确保目标 服务组 存在
        service = Service()
        service.id = request.json.get('service_id', 1)
        service.get()

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

        # http://man7.org/linux/man-pages/man8/tc.8.html
        # 如果带宽大于 tc 所控最大速率，则置其为无限带宽
        # 34359738360 等于 tc 最大可控字节速率，换算出的比特位
        if bandwidth > 34359738360:
            bandwidth = 0

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

            guest.ip = db.r.spop(app_config['ip_available_set'])
            db.r.sadd(app_config['ip_used_set'], guest.ip)

            guest.network = config.vm_network
            guest.manage_network = config.vm_manage_network

            guest.vnc_port = db.r.spop(app_config['vnc_port_available_set'])
            db.r.sadd(app_config['vnc_port_used_set'], guest.vnc_port)

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

            if node_id is None:
                # 在可用计算节点中平均分配任务
                chosen_host = available_hosts[quantity % available_hosts.__len__()]

            else:
                chosen_host = available_hosts_mapping_by_node_id[node_id]

            guest.node_id = chosen_host['node_id']
            guest.service_id = service.id

            guest_xml = GuestXML(host=chosen_host, guest=guest, disk=disk, config=config,
                                 os_type=os_template_profile.os_type)
            guest.xml = guest_xml.get_domain()

            guest.node_id = int(guest.node_id)
            guest.create()

            ssh_key_guest_mapping.guest_uuid = guest.uuid

            if ssh_keys_id.__len__() > 0:
                for ssh_key_id in ssh_keys_id:
                    ssh_key_guest_mapping.ssh_key_id = ssh_key_id
                    ssh_key_guest_mapping.create()

            if os_template_profile.os_distro == 'coreos':
                config.netmask = IP(guest.ip).make_net(config.netmask).prefixlen().__str__()

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

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        # 取全部活着的 hosts
        available_hosts = Host.get_available_hosts(nonrandom=None)

        if available_hosts.__len__() == 0:
            ret['state'] = ji.Common.exchange_state(50351)
            return ret

        available_hosts_mapping_by_node_id = dict()

        for host in available_hosts:
            if host['node_id'] not in available_hosts_mapping_by_node_id:
                available_hosts_mapping_by_node_id[host['node_id']] = host

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

            # 忽略宕机计算节点 上面的 虚拟机 迁移请求
            # 忽略目标计算节点 等于 当前所在 计算节点 的虚拟机 迁移请求
            if guest.node_id.__str__() not in available_hosts_mapping_by_node_id or \
                    available_hosts_mapping_by_node_id[guest.node_id.__str__()]['hostname'] == destination_host:
                continue

            message = {
                '_object': 'guest',
                'action': 'migrate',
                'uuid': uuid,
                'node_id': guest.node_id,
                'storage_mode': config.storage_mode,
                'duri': 'qemu+ssh://' + destination_host + '/system'
            }

            Utils.emit_instruction(message=json.dumps(message))

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

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    if -1 == uuids.find(','):
        if 'ssh_keys' not in ret['data']:
            ret['data']['ssh_keys'] = list()

        if ret['data']['uuid'] in guest_uuid_ssh_key_id_mapping:
            for ssh_key_id in guest_uuid_ssh_key_id_mapping[ret['data']['uuid']]:

                if ssh_key_id not in ssh_key_id_mapping:
                    continue

                ret['data']['ssh_keys'].append(ssh_key_id_mapping[ssh_key_id])

            if not hosts_mapping_by_node_id[ret['data']['node_id']]['alive']:
                ret['data']['status'] = GuestState.no_state.value

    else:
        for i, guest in enumerate(ret['data']):
            if 'ssh_keys' not in ret['data'][i]:
                ret['data'][i]['ssh_keys'] = list()

            if ret['data'][i]['uuid'] in guest_uuid_ssh_key_id_mapping:
                for ssh_key_id in guest_uuid_ssh_key_id_mapping[ret['data'][i]['uuid']]:

                    if ssh_key_id not in ssh_key_id_mapping:
                        continue

                    ret['data'][i]['ssh_keys'].append(ssh_key_id_mapping[ssh_key_id])

            if not hosts_mapping_by_node_id[ret['data'][i]['node_id']]['alive']:
                ret['data'][i]['status'] = GuestState.no_state.value

    return ret


def exchange_guest_os_templates_logo(os_templates_image_mapping_by_id=None, os_templates_profile_mapping_by_id=None,
                                     os_template_image_id=None):
    assert isinstance(os_templates_image_mapping_by_id, dict)
    assert isinstance(os_templates_profile_mapping_by_id, dict)
    assert isinstance(os_template_image_id, int)

    if os_templates_image_mapping_by_id[os_template_image_id]['logo'] == "":
        logo = os_templates_profile_mapping_by_id[os_templates_image_mapping_by_id[os_template_image_id]['os_template_profile_id']]['icon']
    else:
        logo = os_templates_image_mapping_by_id[os_template_image_id]['logo']

    label = os_templates_image_mapping_by_id[os_template_image_id]['label']
    return logo, label


def format_guest_status(_status, progress):
    from jimvc.models import GuestState

    color = 'FF645B'
    icon = 'glyph-icon icon-bolt'
    desc = '未知状态'

    if _status == GuestState.booting.value:
        color = '00BBBB'
        icon = 'glyph-icon icon-circle'
        desc = '启动中'

    elif _status == GuestState.running.value:
        color = '00BB00'
        icon = 'glyph-icon icon-circle'
        desc = '运行中'

    elif _status == GuestState.creating.value:
        color = 'FFC543'
        icon = 'glyph-icon icon-spinner'
        desc = ' '.join(['创建中', str(progress) + '%'])

    elif _status == GuestState.blocked.value:
        color = '3D4245'
        icon = 'glyph-icon icon-minus-square'
        desc = '被阻塞'

    elif _status == GuestState.paused.value:
        color = 'B7B904'
        icon = 'glyph-icon icon-pause'
        desc = '暂停'

    elif _status == GuestState.shutdown.value:
        color = '4E5356'
        icon = 'glyph-icon icon-terminal'
        desc = '关闭'

    elif _status == GuestState.shutoff.value:
        color = 'FFC543'
        icon = 'glyph-icon icon-plug'
        desc = '断电'

    elif _status == GuestState.crashed.value:
        color = '9E2927'
        icon = 'glyph-icon icon-question'
        desc = '已崩溃'

    elif _status == GuestState.pm_suspended.value:
        color = 'FCFF07'
        icon = 'glyph-icon icon-anchor'
        desc = '悬挂'

    elif _status == GuestState.migrating.value:
        color = '1CF5E7'
        icon = 'glyph-icon icon-space-shuttle'
        desc = '迁移中'

    elif _status == GuestState.dirty.value:
        color = 'FF0707'
        icon = 'glyph-icon icon-remove'
        desc = '创建失败，待清理'

    else:
        pass

    return '<span class="{icon}" style="color: #{color};">&nbsp;&nbsp;{desc}</span>'.format(
        icon=icon, color=color, desc=desc)


def exchange_guest_bandwidth(bandwidth=None):
    assert isinstance(bandwidth, int)

    if bandwidth == 0:
        bandwidth = '<span style="font-size: 16px;" title="无限带宽">&nbsp;∞</span>'

    elif 0 < bandwidth < 1000 ** 2:
        bandwidth = str(bandwidth // 1000) + ' Kbps'

    elif 1000 ** 2 <= bandwidth < 1000 ** 3:
        bandwidth = str(bandwidth // 1000 ** 2) + ' Mbps'

    else:
        bandwidth = str(bandwidth // 1000 ** 3) + ' Gbps'

    return bandwidth


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

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    os_templates_image, _ = OSTemplateImage.get_by_filter()
    os_templates_image_mapping_by_id = dict()
    for os_template_image in os_templates_image:
        os_templates_image_mapping_by_id[os_template_image['id']] = os_template_image

    os_templates_profile, _ = OSTemplateProfile.get_by_filter()
    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

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

        if not hosts_mapping_by_node_id[ret['data'][i]['node_id']]['alive']:
            ret['data'][i]['status'] = GuestState.no_state.value

        ret['data'][i]['hostname'] = hosts_mapping_by_node_id[guest['node_id']]['hostname']

        ret['data'][i]['html'] = dict()
        ret['data'][i]['html']['logo'], ret['data'][i]['html']['os_template_label'] = exchange_guest_os_templates_logo(
            os_templates_image_mapping_by_id=os_templates_image_mapping_by_id,
            os_templates_profile_mapping_by_id=os_templates_profile_mapping_by_id,
            os_template_image_id=guest['os_template_image_id'])

        ret['data'][i]['html']['status'] = format_guest_status(_status=guest['status'], progress=guest['progress'])
        ret['data'][i]['html']['bandwidth'] = exchange_guest_bandwidth(bandwidth=guest['bandwidth'])

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

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    os_templates_image, _ = OSTemplateImage.get_by_filter()
    os_templates_image_mapping_by_id = dict()
    for os_template_image in os_templates_image:
        os_templates_image_mapping_by_id[os_template_image['id']] = os_template_image

    os_templates_profile, _ = OSTemplateProfile.get_by_filter()
    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

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

        if not hosts_mapping_by_node_id[ret['data'][i]['node_id']]['alive']:
            ret['data'][i]['status'] = GuestState.no_state.value

        ret['data'][i]['hostname'] = hosts_mapping_by_node_id[guest['node_id']]['hostname']

        ret['data'][i]['html'] = dict()
        ret['data'][i]['html']['logo'], ret['data'][i]['html']['os_template_label'] = exchange_guest_os_templates_logo(
            os_templates_image_mapping_by_id=os_templates_image_mapping_by_id,
            os_templates_profile_mapping_by_id=os_templates_profile_mapping_by_id,
            os_template_image_id=guest['os_template_image_id'])

        ret['data'][i]['html']['status'] = format_guest_status(_status=guest['status'], progress=guest['progress'])
        ret['data'][i]['html']['bandwidth'] = exchange_guest_bandwidth(bandwidth=guest['bandwidth'])

    return ret


@Utils.dumps2response
def r_distribute_count():
    from jimvc.models import Guest
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
def r_update(uuids):

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = list()

    args_rules = [
        Rules.UUIDS.value
    ]

    if 'remark' in request.json:
        args_rules.append(
            Rules.REMARK.value,
        )

    if args_rules.__len__() < 2:
        return ret

    request.json['uuids'] = uuids

    try:
        ji.Check.previewing(args_rules, request.json)
        guest = Guest()
        # 检测所指定的 UUDIs 实例都存在
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')
            guest.remark = request.json.get('remark', guest.remark)

            guest.update()
            guest.get()

            ret['data'].append(guest.__dict__)

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

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        bandwidth = int(bandwidth)

        if bandwidth_unit == 'k':
            bandwidth = bandwidth * 1000

        elif bandwidth_unit == 'm':
            bandwidth = bandwidth * 1000 ** 2

        elif bandwidth_unit == 'g':
            bandwidth = bandwidth * 1000 ** 3

        else:
            ret['state'] = ji.Common.exchange_state(41203)
            return ret

        # http://man7.org/linux/man-pages/man8/tc.8.html
        # 如果带宽大于 tc 所控最大速率，则置其为无限带宽
        # 34359738360 等于 tc 最大可控字节速率，换算出的比特位
        if bandwidth > 34359738360:
            bandwidth = 0

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

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_adjust_ability(uuids, cpu, memory):
    args_rules = [
        Rules.UUIDS.value,
        Rules.CPU.value,
        Rules.MEMORY.value,
    ]

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        cpu = int(cpu)
        memory = int(memory)

        ji.Check.previewing(args_rules, {'uuids': uuids, 'cpu': cpu, 'memory': memory})

        not_ready_yet_of_guests = list()

        guest = Guest()

        # 检测所指定的 UUDIs 实例都存在。且状态都为可以操作状态（即关闭状态）。
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

            if guest.status != status.GuestState.shutoff.value:
                not_ready_yet_of_guests.append(guest.__dict__)

        if not_ready_yet_of_guests.__len__() > 0:
            ret['state'] = ji.Common.exchange_state(41261)
            ret['data'] = not_ready_yet_of_guests
            return ret

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')
            guest.cpu = cpu
            guest.memory = memory

            message = {
                '_object': 'guest',
                'action': 'adjust_ability',
                'uuid': guest.uuid,
                'node_id': guest.node_id,
                'cpu': guest.cpu,
                'memory': guest.memory,
                'passback_parameters': {'cpu': guest.cpu, 'memory': guest.memory}
            }

            Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_change_prepared_by(uuids, service_id):

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = list()

    args_rules = [
        Rules.UUIDS.value,
        Rules.SERVICE_ID_IN_URL.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids, 'service_id': service_id})

        guest = Guest()

        # 检测所指定的 UUDIs 实例都存在
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')
            guest.service_id = int(service_id)

            guest.update()
            guest.get()

            ret['data'].append(guest.__dict__)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_refresh_guest_state():
    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        # 取全部活着的 hosts
        available_hosts = Host.get_available_hosts(nonrandom=None)

        if available_hosts.__len__() == 0:
            ret['state'] = ji.Common.exchange_state(50351)
            return ret

        for host in available_hosts:
            message = {
                '_object': 'global',
                'action': 'refresh_guest_state',
                'node_id': host['node_id']
            }

            Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    guests_url = url_for('api_guests.r_get_by_filter', _external=True)
    if keyword is not None:
        guests_url = url_for('api_guests.r_content_search', _external=True)

    if args.__len__() > 0:
        guests_url = guests_url + '?' + '&'.join(args)

    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    os_templates_image, _ = OSTemplateImage.get_by_filter()
    os_templates_image_mapping_by_id = dict()
    for os_template_image in os_templates_image:
        os_templates_image_mapping_by_id[os_template_image['id']] = os_template_image

    os_templates_profile, _ = OSTemplateProfile.get_by_filter()
    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

    last_page = int(ceil(guests_ret['paging']['total'] / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'guests': guests_ret['data'],
        'os_templates_image_mapping_by_id': os_templates_image_mapping_by_id,
        'os_templates_profile_mapping_by_id': os_templates_profile_mapping_by_id,
        'hosts_mapping_by_node_id': hosts_mapping_by_node_id,
        'paging': guests_ret['paging'],
        'page': page,
        'page_size': page_size,
        'keyword': keyword,
        'pages': pages,
        'last_page': last_page
    }

    return ret


@Utils.dumps2response
def r_vnc(uuid):

    guest_ret = guest_base.get(ids=uuid, ids_rule=Rules.UUID.value, by_field='uuid')

    if '200' != guest_ret['state']['code']:
        return guest_ret

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    port = random.randrange(50000, 60000)
    while True:
        if not Utils.port_is_opened(port=port):
            break

        port = random.randrange(50000, 60000)

    payload = {'listen_port': port, 'target_host': hosts_mapping_by_node_id[guest_ret['data']['node_id']]['hostname'],
               'target_port': guest_ret['data']['vnc_port']}

    db.r.rpush(app_config['ipc_queue'], json.dumps(payload, ensure_ascii=False))
    time.sleep(1)

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'port': port,
        'vnc_password': guest_ret['data']['vnc_password']
    }

    return ret


@Utils.dumps2response
def r_detail(uuid):

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_node_id = dict()
    for host in hosts_ret['data']:
        hosts_mapping_by_node_id[int(host['node_id'])] = host

    guest = Guest()
    guest.uuid = uuid
    guest.get_by(field='uuid')
    guest.ssh_keys = list()

    rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['guest_uuid', 'in', guest.uuid]))

    ssh_keys_id = list()

    for row in rows:
        if row['ssh_key_id'] not in ssh_keys_id:
            ssh_keys_id.append(row['ssh_key_id'].__str__())

    rows, _ = SSHKey.get_by_filter(filter_str=':'.join(['id', 'in', ','.join(ssh_keys_id)]))

    for row in rows:
        row['url'] = url_for('v_ssh_keys.show')

        if row['id'].__str__() not in ssh_keys_id:
            continue

        guest.ssh_keys.append(row)

    os_template_image = OSTemplateImage()
    os_template_image.id = guest.os_template_image_id.__str__()
    os_template_image.get()

    os_template_profiles, _ = OSTemplateProfile.get_by_filter()

    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_template_profiles:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

    disks_url = url_for('api_disks.r_get_by_filter', filter='guest_uuid:in:' + guest.uuid, _external=True)
    disks_ret = requests.get(url=disks_url, cookies=request.cookies)
    disks = json.loads(disks_ret.content)['data']

    if not hosts_mapping_by_node_id[guest.node_id]['alive']:
        guest.status = GuestState.no_state.value

    config = Config()
    config.id = 1
    config.get()

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'uuid': uuid,
        'guest': guest.__dict__,
        'os_template_image': os_template_image.__dict__,
        'os_templates_profile_mapping_by_id': os_templates_profile_mapping_by_id,
        'hosts_mapping_by_node_id': hosts_mapping_by_node_id,
        'disks': disks,
        'config': config.__dict__
    }

    return ret


