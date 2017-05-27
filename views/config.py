#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, g
from flask import request
import jimit as ji
import json

from models import Config
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'config',
    __name__,
    url_prefix='/api/config'
)


@Utils.dumps2response
def r_create():

    config = Config()

    args_rules = [
        Rules.GLUSTERFS_VOLUME.value,
        Rules.STORAGE_PATH.value,
        Rules.VM_NETWORK.value,
        Rules.VM_MANAGE_NETWORK.value,
        Rules.START_IP.value,
        Rules.END_IP.value,
        Rules.START_VNC_PORT.value,
        Rules.NETMASK.value,
        Rules.GATEWAY.value,
        Rules.DNS1.value,
        Rules.DNS2.value,
        Rules.RSA_PRIVATE.value,
        Rules.RSA_PUBLIC.value
    ]

    config.id = 1
    config.glusterfs_volume = request.json.get('glusterfs_volume')
    config.storage_path = request.json.get('storage_path')
    config.vm_network = request.json.get('vm_network')
    config.vm_manage_network = request.json.get('vm_manage_network')
    config.start_ip = request.json.get('start_ip')
    config.end_ip = request.json.get('end_ip')
    config.start_vnc_port = request.json.get('start_vnc_port')
    config.netmask = request.json.get('netmask')
    config.gateway = request.json.get('gateway')
    config.dns1 = request.json.get('dns1')
    config.dns2 = request.json.get('dns2')
    config.rsa_private = request.json.get('rsa_private')
    config.rsa_public = request.json.get('rsa_public')

    try:
        ji.Check.previewing(args_rules, config.__dict__)

        config.check_ip()
        config.generate_available_ip2set()
        config.generate_available_vnc_port()
        config.create()
        g.config = None

        config.id = 1
        config.get()
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = config.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update():

    config = Config()

    args_rules = [
    ]

    if 'glusterfs_volume' in request.json:
        args_rules.append(
            Rules.GLUSTERFS_VOLUME.value,
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

    if 'start_ip' in request.json:
        args_rules.append(
            Rules.START_IP.value,
        )

    if 'end_ip' in request.json:
        args_rules.append(
            Rules.END_IP.value,
        )

    if 'start_vnc_port' in request.json:
        args_rules.append(
            Rules.START_VNC_PORT.value,
        )

    if 'netmask' in request.json:
        args_rules.append(
            Rules.NETMASK.value,
        )

    if 'gateway' in request.json:
        args_rules.append(
            Rules.GATEWAY.value,
        )

    if 'dns1' in request.json:
        args_rules.append(
            Rules.DNS1.value,
        )

    if 'dns2' in request.json:
        args_rules.append(
            Rules.DNS2.value,
        )

    if 'rsa_private' in request.json:
        args_rules.append(
            Rules.RSA_PRIVATE.value,
        )

    if 'rsa_public' in request.json:
        args_rules.append(
            Rules.RSA_PUBLIC.value
        )

    if args_rules.__len__() < 1:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    try:
        config.id = 1
        ji.Check.previewing(args_rules, request.json)
        config.get()

        config.glusterfs_volume = request.json.get('glusterfs_volume', config.glusterfs_volume)
        config.storage_path = request.json.get('storage_path', config.storage_path)
        config.vm_network = request.json.get('vm_network', config.vm_network)
        config.vm_manage_network = request.json.get('vm_manage_network', config.vm_manage_network)
        config.start_ip = request.json.get('start_ip', config.start_ip)
        config.end_ip = request.json.get('end_ip', config.end_ip)
        config.start_vnc_port = request.json.get('start_vnc_port', config.start_vnc_port)
        config.netmask = request.json.get('netmask', config.netmask)
        config.gateway = request.json.get('gateway', config.gateway)
        config.dns1 = request.json.get('dns1', config.dns1)
        config.dns2 = request.json.get('dns2', config.dns2)
        config.rsa_private = request.json.get('rsa_private', config.rsa_private)
        config.rsa_public = request.json.get('rsa_public', config.rsa_public)

        config.check_ip()
        config.generate_available_ip2set()
        config.generate_available_vnc_port()
        config.update()

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

