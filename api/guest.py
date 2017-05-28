#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
from flask import Blueprint
from flask import request
import json
from uuid import uuid4
import jimit as ji

from api.base import Base
from models import DiskState
from models import OSInitWrite
from models.initialize import app, dev_table
from models import Database as db
from models import Config
from models import Disk
from models import Rules
from models import Utils
from models import Guest
from models import OSTemplate
from models import GuestXML
from models import status


__author__ = 'James Iter'
__date__ = '2017/3/22'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'guest',
    __name__,
    url_prefix='/api/guest'
)

blueprints = Blueprint(
    'guests',
    __name__,
    url_prefix='/api/guests'
)


guest_base = Base(the_class=Guest, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.CPU.value,
        Rules.MEMORY.value,
        Rules.OS_TEMPLATE_ID.value,
        Rules.QUANTITY.value,
        Rules.NAME.value,
        Rules.PASSWORD.value,
        Rules.LEASE_TERM.value
    ]

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ji.Check.previewing(args_rules, request.json)

        config = Config()
        config.id = 1
        config.get()

        os_template = OSTemplate()
        os_template.id = request.json.get('os_template_id')
        if not os_template.exist():
            ret['state'] = ji.Common.exchange_state(40450)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template.id.__str__()])
            return ret

        os_template.get()

        os_init_writes, os_init_writes_count = OSInitWrite.get_by_filter(
            filter_str='os_init_id:in:' + os_template.os_init_id.__str__())

        if db.r.scard(app.config['ip_available_set']) < 1:
            ret['state'] = ji.Common.exchange_state(50350)
            return ret

        quantity = request.json.get('quantity')

        while quantity:
            quantity -= 1
            guest = Guest()
            guest.uuid = uuid4().__str__()
            guest.cpu = request.json.get('cpu')
            # 虚拟机内存单位，模板生成方法中已置其为GiB
            guest.memory = request.json.get('memory')
            guest.os_template_id = request.json.get('os_template_id')
            guest.name = request.json.get('name')
            if quantity > 0:
                '-'.join([guest.name, quantity.__str__()])

            guest.password = request.json.get('password')
            if guest.password is None or guest.password.__len__() < 1:
                guest.password = ji.Common.generate_random_code(length=16)

            while guest.name.__len__() < 1 or guest.exist_by('name'):
                guest.name = ji.Common.generate_random_code(length=8)

            guest.ip = db.r.spop(app.config['ip_available_set'])
            db.r.sadd(app.config['ip_used_set'], guest.ip)

            guest.network = config.vm_network
            guest.manage_network = config.vm_manage_network

            guest.vnc_port = db.r.spop(app.config['vnc_port_available_set'])
            db.r.sadd(app.config['vnc_port_used_set'], guest.vnc_port)

            guest.vnc_password = ji.Common.generate_random_code(length=16)

            disk = Disk()
            disk.uuid = guest.uuid
            disk.label = guest.name + '_SystemImage'
            disk.format = 'qcow2'
            disk.sequence = 0
            disk.size = 0
            disk.path = config.storage_path + '/' + disk.uuid + '.' + disk.format
            disk.guest_uuid = ''
            disk.create()

            guest_xml = GuestXML(guest=guest, disk=disk, config=config)
            guest.xml = guest_xml.get_domain()
            guest.create()

            # 替换占位符为有效内容
            _os_init_writes = copy.deepcopy(os_init_writes)
            for k, v in enumerate(_os_init_writes):
                _os_init_writes[k]['content'] = v['content'].replace('{IP}', guest.ip).\
                    replace('{HOSTNAME}', guest.name).\
                    replace('{NETMASK}', config.netmask).\
                    replace('{GATEWAY}', config.gateway).\
                    replace('{DNS1}', config.dns1).\
                    replace('{DNS2}', config.dns2)

            create_vm_msg = {
                'action': 'create_guest',
                'uuid': guest.uuid,
                'name': guest.name,
                'glusterfs_volume': config.glusterfs_volume,
                'template_path': os_template.path,
                'disk': disk.__dict__,
                'writes': _os_init_writes,
                'password': guest.password,
                'xml': guest_xml.get_domain()
            }
            db.r.rpush(app.config['downstream_queue'], json.dumps(create_vm_msg, ensure_ascii=False))

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
            message = {'action': 'reboot', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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
            message = {'action': 'force_reboot', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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
            message = {'action': 'shutdown', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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
            message = {'action': 'force_shutdown', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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

        for uuid in uuids.split(','):
            message = {'action': 'boot', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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
            message = {'action': 'suspend', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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
            message = {'action': 'resume', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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

        # 执行删除操作
        for uuid in uuids.split(','):
            message = {'action': 'delete_guest', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

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

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        # 判断欲挂载的磁盘是否空闲
        if disk.guest_uuid.__len__() > 0:
            ret['state'] = ji.Common.exchange_state(41258)
            return ret

        # 判断 Guest 是否处于可用状态
        if guest.status in (status.GuestState.no_state.value, status.GuestState.dirty.value):
            ret['state'] = ji.Common.exchange_state(41259)
            return ret

        # 取出该 guest 已挂载的磁盘，来做出决定，确定该磁盘的序列
        disk.guest_uuid = guest.uuid
        disks, count = disk.get_by_filter(filter_str='guest_uuid:in:' + guest.uuid)
        disk.sequence = count + 1

        config = Config()
        config.id = 1
        config.get()

        xml = """
            <disk type='network' device='disk'>
                <driver name='qemu' type='qcow2' cache='none'/>
                <source protocol='gluster' name='{0}/DiskPool/{1}.{2}'>
                    <host name='127.0.0.1' port='24007'/>
                </source>
                <target dev='{3}' bus='virtio'/>
            </disk>
        """.format(config.glusterfs_volume, disk.uuid, disk.format,
                   dev_table[disk.sequence])

        message = {'action': 'attach_disk', 'uuid': uuid, 'xml': xml,
                   'passback_parameters': {'disk_uuid': disk.uuid, 'sequence': disk.sequence}}
        Guest.emit_instruction(message=json.dumps(message))

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

        xml = """
            <disk type='network' device='disk'>
                <driver name='qemu' type='qcow2' cache='none'/>
                <source protocol='gluster' name='{0}/DiskPool/{1}.{2}'>
                    <host name='127.0.0.1' port='24007'/>
                </source>
                <target dev='{3}' bus='virtio'/>
            </disk>
        """.format(config.glusterfs_volume, disk.uuid, disk.format,
                   dev_table[disk.sequence])

        message = {'action': 'detach_disk', 'uuid': disk.guest_uuid, 'xml': xml,
                   'passback_parameters': {'disk_uuid': disk.uuid}}
        Guest.emit_instruction(message=json.dumps(message))

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

        for uuid in uuids.split(','):
            message = {'action': 'migrate', 'uuid': uuid, 'duri': 'qemu+ssh://' + destination_host + '/system'}
            Guest.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(uuids):
    return guest_base.get(ids=uuids, ids_rule=Rules.UUIDS.value, by_field='uuid')


@Utils.dumps2response
def r_get_by_filter():
    return guest_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return guest_base.content_search()


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

        guest.remark = request.json.get('remark', guest.name)

        guest.update()
        guest.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = guest.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)
