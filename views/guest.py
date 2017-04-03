#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
from flask import Blueprint
from flask import request, g
import json
from uuid import uuid4
import jimit as ji

from models import OSInitWrite
from models.initialize import app
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

        if g.config is None:
            config = Config()
            config.id = 1
            config.get()
            g.config = config

        assert isinstance(g.config, Config)

        os_template = OSTemplate()
        os_template.id = request.json.get('os_template_id')
        if not os_template.exist():
            ret['state'] = ji.Common.exchange_state(40450)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template.id])
            return ret

        os_template.get()

        os_init_writes = OSInitWrite.get_by_filter(
            filter_str='os_init_id:in:' + os_template.os_init_id.__str__())

        if g.r.scard(app.config['ip_available_set']) < 1:
            ret['state'] = ji.Common.exchange_state(50350)
            return ret

        quantity = request.json.get('quantity')

        while quantity:
            quantity -= 1
            guest = Guest()
            guest.uuid = uuid4().__str__()
            guest.cpu = request.json.get('cpu')
            # 虚拟机内存单位默认KiB，所以这个乘1024的平方，使得用户填入的单位变为GiB
            guest.memory = request.json.get('memory') * 1024 * 1024
            guest.os_template_id = request.json.get('os_template_id')
            guest.name = request.json.get('name')

            guest.password = request.json.get('password')
            if guest.password is None or guest.password.__len__() < 1:
                guest.password = ji.Common.generate_random_code(length=16)

            while guest.name.__len__() < 1 or guest.exist_by('name'):
                guest.name = ji.Common.generate_random_code(length=8)

            guest.ip = g.r.spop(app.config['ip_available_set'])
            g.r.sadd(app.config['ip_used_set'], guest.ip)

            guest.network = g.config.vm_network
            guest.manage_network = g.config.vm_manage_network

            guest.vnc_port = g.r.spop(app.config['vnc_port_available_set'])
            g.r.sadd(app.config['vnc_port_used_set'], guest.vnc_port)

            guest.vnc_password = ji.Common.generate_random_code(length=16)

            guest_disks = list()
            guest_disks.append({'label': uuid4(), 'size': -1, 'format': 'qcow2'})

            for i, disk in enumerate(request.json.get('disks')):
                guest_disk = GuestDisk()

                guest_disk.size = disk.get('size')
                # TODO: 设定磁盘最大大小
                if not isinstance(guest_disk.size, int) or guest_disk.size < 1:
                    continue

                guest_disk.guest_uuid = guest.uuid
                guest_disk.label = uuid4()
                guest_disk.sequence = i + 1
                guest_disk.format = 'qcow2'
                guest_disk.create()

                guest_disks.append({'label': guest_disk.label, 'size': guest_disk.size, 'format': guest_disk.format})

            guest.create()
            guest_xml = GuestXML(guest=guest, disks=guest_disks, g_config=g.config)
            guest_xml.get_domain()

            # 替换占位符为有效内容
            _os_init_writes = copy.deepcopy(os_init_writes)
            for k, v in _os_init_writes:
                _os_init_writes[k] = v.replace('{IP}', guest.ip).\
                    replace('{HOSTNAME}', guest.name).\
                    replace('{NETMASK}', g.config.netmask).\
                    replace('{GATEWAY}', g.config.gateway).\
                    replace('{DNS1}', g.config.dns1).\
                    replace('{DNS2}', g.config.dns2)

            create_vm_msg = {
                'uuid': guest.uuid,
                'glusterfs_volume': g.config.glusterfs_volume,
                'template_path': 'template_pool/' + os_template.name,
                'guest_disks': guest_disks,
                'writes': _os_init_writes,
                'password': guest.password,
                'xml': guest_xml.get_domain()
            }
            g.r.rpush(app.config['vm_create_queue'], json.dumps(create_vm_msg, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

