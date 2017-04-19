#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
from flask import Blueprint
from flask import request
import json
from uuid import uuid4
import jimit as ji

from models import OSInitWrite
from models.initialize import app, dev_table
from models import Database as db
from models import Config
from models import GuestDisk
from models import Rules
from models import Utils
from models import Guest
from models import OSTemplate
from models import GuestXML


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


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.CPU.value,
        Rules.MEMORY.value,
        Rules.OS_TEMPLATE_ID.value,
        Rules.DISKS.value,
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
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template.id])
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

            guest_disks = list()
            guest_disks.append({'label': uuid4().__str__(), 'size': -1, 'format': 'qcow2'})

            for i, disk in enumerate(request.json.get('disks')):
                guest_disk = GuestDisk()

                guest_disk.size = disk.get('size')
                # TODO: 设定磁盘最大大小
                if not isinstance(guest_disk.size, int) or guest_disk.size < 1:
                    continue

                guest_disk.guest_uuid = guest.uuid
                guest_disk.label = uuid4().__str__()
                guest_disk.sequence = i + 1
                guest_disk.format = 'qcow2'
                guest_disk.create()

                guest_disks.append({'label': guest_disk.label, 'size': guest_disk.size, 'format': guest_disk.format})

            guest_xml = GuestXML(guest=guest, disks=guest_disks, config=config)
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
                'action': 'create_vm',
                'uuid': guest.uuid,
                'name': guest.name,
                'glusterfs_volume': config.glusterfs_volume,
                'template_path': 'template_pool/' + os_template.name,
                'guest_disks': guest_disks,
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

    try:
        ji.Check.previewing(args_rules, {'uuids': uuids})

        guest = Guest()
        for uuid in uuids.split(','):
            guest.uuid = uuid
            guest.get_by('uuid')

        for uuid in uuids.split(','):
            message = {'action': 'delete', 'uuid': uuid}
            Guest.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_disk_resize(device_node_uuid, size):

    args_rules = [
        Rules.DEVICE_NODE_UUID.value,
        Rules.DISK_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'device_node_uuid': device_node_uuid, 'size': size})

        guest_disk = GuestDisk()
        guest_disk.label = device_node_uuid
        guest_disk.get_by('label')

        message = {'action': 'disk-resize', 'uuid': guest_disk.guest_uuid,
                   'device_node': dev_table[guest_disk.sequence], 'size': size}
        Guest.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_create_disk(size):

    args_rules = [
        Rules.DISK_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'size': size})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        size = int(size)

        if not isinstance(size, int) or size < 1:
            ret['state'] = ji.Common.exchange_state(41255)
            return ret

        guest_disk = GuestDisk()
        guest_disk.guest_uuid = ''
        guest_disk.size = size
        guest_disk.label = uuid4().__str__()
        guest_disk.sequence = -1
        guest_disk.format = 'qcow2'
        guest_disk.create()

        config = Config()
        config.id = 1
        config.get()

        image_path = '/'.join(['DiskPool', guest_disk.label + '.' + guest_disk.format])

        message = {'action': 'create_disk', 'glusterfs_volume': config.glusterfs_volume,
                   'image_path': image_path, 'size': guest_disk.size}

        db.r.rpush(app.config['downstream_queue'], json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_attach_disk(uuid, size):

    args_rules = [
        Rules.UUID.value,
        Rules.DISK_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid, 'size': size})

        guest = Guest()
        guest.uuid = uuid
        guest.get_by('uuid')

        guest_disk = GuestDisk()
        guest_disk.guest_uuid = guest.uuid
        disks, count = guest_disk.get_all()

        guest_disk.size = int(size)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if not isinstance(guest_disk.size, int) or guest_disk.size < 1:
            ret['state'] = ji.Common.exchange_state(41255)
            return ret

        config = Config()
        config.id = 1
        config.get()

        guest_disk.label = uuid4().__str__()
        guest_disk.sequence = count + 1
        guest_disk.format = 'qcow2'
        guest_disk.create()

        xml = """
            <disk type='network' device='disk'>
                <driver name='qemu' type='qcow2' cache='none'/>
                <source protocol='gluster' name='{0}/VMs/{1}/{2}.{3}'>
                    <host name='127.0.0.1' port='24007'/>
                </source>
                <target dev='{4}' bus='virtio'/>
            </disk>
        """.format(config.glusterfs_volume, guest.name, guest_disk.label, guest_disk.format,
                   dev_table[guest_disk.sequence])

        message = {'action': 'attach_disk', 'uuid': uuid, 'xml': xml,
                   'disk': {'label': guest_disk.label, 'size': guest_disk.size, 'format': guest_disk.format}}
        Guest.emit_instruction(message=json.dumps(message))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_detach_disk(uuid):

    args_rules = [
        Rules.UUID.value
    ]

    try:
        ji.Check.previewing(args_rules, {'uuid': uuid})

        guest = Guest()
        guest.uuid = uuid
        guest.get_by('uuid')

        message = {'action': 'detach_disk', 'uuid': uuid}
        Guest.emit_instruction(message=json.dumps(message))

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
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

