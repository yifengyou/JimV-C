#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
from flask import Blueprint, request, url_for
import json
import jimit as ji

from jimvc.models import Config
from jimvc.models import Utils, Guest
from jimvc.models import Rules
from jimvc.models import VLAN
from jimvc.models import Host

from base import Base


__author__ = 'James Iter'
__date__ = '2019-03-12'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2019 by James Iter.'


blueprint = Blueprint(
    'api_vlan',
    __name__,
    url_prefix='/api/vlan'
)

blueprints = Blueprint(
    'api_vlans',
    __name__,
    url_prefix='/api/vlans'
)


vlan_base = Base(the_class=VLAN, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.VLAN_ID.value,
        Rules.LABEL.value,
        Rules.DESCRIPTION.value
    ]

    vlan = VLAN()
    vlan.vlan_id = request.json.get('vlan_id')
    vlan.label = request.json.get('label')
    vlan.description = request.json.get('description', '')

    try:
        ji.Check.previewing(args_rules, vlan.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if vlan.exist_by('vlan_id'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': Vlan ID: ', str(vlan.vlan_id)])
            return ret

        vlan.create()
        vlan.get()

        # 取全部活着的 hosts
        available_hosts = Host.get_available_hosts(nonrandom=None)
        for host in available_hosts:
            message = {
                '_object': 'vlan',
                'action': 'create',
                'uuid': None,
                'node_id': host['node_id'],
                'vlan_id': vlan.vlan_id,
                'passback_parameters': {'vlan_id': vlan.vlan_id}
            }

            Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        ret['data'] = vlan.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(ids):

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = list()

    args_rules = [
        Rules.IDS.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if 'description' in request.json:
        args_rules.append(
            Rules.DESCRIPTION.value,
        )

    if args_rules.__len__() < 2:
        return ret

    request.json['ids'] = ids

    try:
        ji.Check.previewing(args_rules, request.json)

        vlan = VLAN()

        # 检测所指定的 vlan 都存在
        for _id in ids.split(','):
            vlan.id = _id
            vlan.get()

        for _id in ids.split(','):
            vlan.id = _id
            vlan.get()
            vlan.label = request.json.get('label', vlan.label)
            vlan.description = request.json.get('description', vlan.description)

            vlan.update()
            vlan.get()

            ret['data'].append(vlan.__dict__)

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(ids):
    ret = vlan_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')

    if '200' != ret['state']['code']:
        return ret

    config = Config()
    config.id = 1
    config.get()

    default_bridge = VLAN()
    default_bridge.id = 0
    default_bridge.vlan_id = -1
    default_bridge.label = u'默认网桥'
    default_bridge.description = u'系统初始化时的默认网桥。在系统中可见为：' + config.vm_network + u'。'
    default_bridge.create_time = 0

    ret['data'].insert(0, default_bridge.__dict__)

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies, verify=False)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_vlan_bridge = dict()
    for vlan in ret['data']:
        vlan_bridge_name = 'vlan' + vlan['vlan_id'].__str__()
        vlan_bond_name = 'bond0.' + vlan['vlan_id'].__str__()

        if vlan_bridge_name not in hosts_mapping_by_vlan_bridge:
            hosts_mapping_by_vlan_bridge[vlan_bridge_name] = list()

        for host in hosts_ret['data']:
            if vlan_bridge_name in host['vlans'] and vlan_bond_name in host['vlans']:
                hosts_mapping_by_vlan_bridge[vlan_bridge_name].append(host)

    hosts = hosts_ret['data']
    posts = hosts.__len__()

    for i, vlan in enumerate(ret['data']):
        if ret['data'][i]['vlan_id'] == -1:
            ret['data'][i]['posts'] = posts
            ret['data'][i]['arrival'] = posts

        else:
            vlan_bridge_name = 'vlan' + vlan['vlan_id'].__str__()
            ret['data'][i]['posts'] = posts
            ret['data'][i]['arrival'] = hosts_mapping_by_vlan_bridge[vlan_bridge_name].__len__()

    return ret


@Utils.dumps2response
def r_get_by_filter():
    ret = vlan_base.get_by_filter()

    if '200' != ret['state']['code']:
        return ret

    config = Config()
    config.id = 1
    config.get()

    default_bridge = VLAN()
    default_bridge.id = 0
    default_bridge.vlan_id = -1
    default_bridge.label = u'默认网桥'
    default_bridge.description = u'系统初始化时的默认网桥。在系统中可见为：' + config.vm_network + u'。'
    default_bridge.create_time = 0

    ret['data'].insert(0, default_bridge.__dict__)

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies, verify=False)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_vlan_bridge = dict()
    for vlan in ret['data']:
        vlan_bridge_name = 'vlan' + vlan['vlan_id'].__str__()
        vlan_bond_name = 'bond0.' + vlan['vlan_id'].__str__()

        if vlan_bridge_name not in hosts_mapping_by_vlan_bridge:
            hosts_mapping_by_vlan_bridge[vlan_bridge_name] = list()

        for host in hosts_ret['data']:
            if vlan_bridge_name in host['vlans'] and vlan_bond_name in host['vlans']:
                hosts_mapping_by_vlan_bridge[vlan_bridge_name].append(host)

    hosts = hosts_ret['data']
    posts = hosts.__len__()

    for i, vlan in enumerate(ret['data']):
        if ret['data'][i]['vlan_id'] == -1:
            ret['data'][i]['posts'] = posts
            ret['data'][i]['arrival'] = posts

        else:
            vlan_bridge_name = 'vlan' + vlan['vlan_id'].__str__()
            ret['data'][i]['posts'] = posts
            ret['data'][i]['arrival'] = hosts_mapping_by_vlan_bridge[vlan_bridge_name].__len__()

    return ret


@Utils.dumps2response
def r_content_search():
    ret = vlan_base.content_search()

    if '200' != ret['state']['code']:
        return ret

    config = Config()
    config.id = 1
    config.get()

    default_bridge = VLAN()
    default_bridge.id = 0
    default_bridge.vlan_id = -1
    default_bridge.label = u'默认网桥'
    default_bridge.description = u'系统初始化时的默认网桥。在系统中可见为：' + config.vm_network + u'。'
    default_bridge.create_time = 0

    ret['data'].insert(0, default_bridge.__dict__)

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies, verify=False)
    hosts_ret = json.loads(hosts_ret.content)

    hosts_mapping_by_vlan_bridge = dict()
    for vlan in ret['data']:
        vlan_bridge_name = 'vlan' + vlan['vlan_id'].__str__()
        vlan_bond_name = 'bond0.' + vlan['vlan_id'].__str__()

        if vlan_bridge_name not in hosts_mapping_by_vlan_bridge:
            hosts_mapping_by_vlan_bridge[vlan_bridge_name] = list()

        for host in hosts_ret['data']:
            if vlan_bridge_name in host['vlans'] and vlan_bond_name in host['vlans']:
                hosts_mapping_by_vlan_bridge[vlan_bridge_name].append(host)

    hosts = hosts_ret['data']
    posts = hosts.__len__()

    for i, vlan in enumerate(ret['data']):
        if ret['data'][i]['vlan_id'] == -1:
            ret['data'][i]['posts'] = posts
            ret['data'][i]['arrival'] = posts

        else:
            vlan_bridge_name = 'vlan' + vlan['vlan_id'].__str__()
            ret['data'][i]['posts'] = posts
            ret['data'][i]['arrival'] = hosts_mapping_by_vlan_bridge[vlan_bridge_name].__len__()

    return ret


@Utils.dumps2response
def r_delete(ids):
    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    args_rules = [
        Rules.IDS.value
    ]

    try:

        ji.Check.previewing(args_rules, {'ids': ids})

        vlan = VLAN()

        # 检测所指定的 vlan 都存在
        for _id in ids.split(','):
            vlan.id = _id
            vlan.get()

            guests, _ = Guest.get_by_filter(filter_str=':'.join(['vlan_id', 'eq', vlan.vlan_id.__str__()]))

            # 检测 vlan 中是否存在 虚拟机，若存在，则拒绝删除操作。
            if guests.__len__() > 0:

                guests_info = ''
                for guest in guests:
                    guests_info += guest['label'] + ',' + guest['uuid'] + '.'

                ret['state'] = ji.Common.exchange_state(41262)
                ret['state']['sub']['zh-cn'] = ''.join([
                    ret['state']['sub']['zh-cn'], u': Vlan ID: ', vlan.vlan_id, u': Guests: ', guests_info])

                return ret

        for _id in ids.split(','):
            vlan.id = _id
            vlan.get()

            # 取全部活着的 hosts
            available_hosts = Host.get_available_hosts(nonrandom=None)
            for host in available_hosts:
                message = {
                    '_object': 'vlan',
                    'action': 'delete',
                    'uuid': None,
                    'node_id': host['node_id'],
                    'vlan_id': vlan.vlan_id,
                    'passback_parameters': {'id': vlan.id, 'vlan_id': vlan.vlan_id}
                }

                Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_force_delete(ids):
    args_rules = [
        Rules.IDS.value
    ]

    try:

        ji.Check.previewing(args_rules, {'ids': ids})

        vlan = VLAN()

        # 检测所指定的 vlan 都存在
        for _id in ids.split(','):
            vlan.id = _id
            vlan.get()

            guests, _ = Guest.get_by_filter(filter_str=':'.join(['vlan_id', 'eq', vlan.vlan_id.__str__()]))

            # 检测 vlan 中是否存在 虚拟机，若存在，则拒绝删除操作。
            if guests.__len__() > 0:

                guests_info = ''
                for guest in guests:
                    guests_info += guest['label'] + ',' + guest['uuid'] + '.'

                ret = dict()
                ret['state'] = ji.Common.exchange_state(41262)
                ret['state']['sub']['zh-cn'] = ''.join([
                    ret['state']['sub']['zh-cn'], u': Vlan ID: ', vlan.vlan_id, u': Guests: ', guests_info])

                return ret

        for _id in ids.split(','):
            vlan.id = _id
            vlan.get()

            # 取全部活着的 hosts
            available_hosts = Host.get_available_hosts(nonrandom=None)
            for host in available_hosts:
                message = {
                    '_object': 'vlan',
                    'action': 'delete',
                    'uuid': None,
                    'node_id': host['node_id'],
                    'vlan_id': vlan.vlan_id,
                    'passback_parameters': {'id': vlan.id, 'vlan_id': vlan.vlan_id}
                }

                Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

    except ji.PreviewingError, e:
        return json.loads(e.message)

    return vlan_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_sync():
    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        vlans, _ = VLAN.get_all()

        # 取全部活着的 hosts
        available_hosts = Host.get_available_hosts(nonrandom=None)

        for vlan in vlans:
            for host in available_hosts:
                message = {
                    '_object': 'vlan',
                    'action': 'create',
                    'uuid': None,
                    'node_id': host['node_id'],
                    'vlan_id': vlan['vlan_id'],
                    'passback_parameters': {'vlan_id': vlan['vlan_id']}
                }

                Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)

