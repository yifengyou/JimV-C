#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, request
import json
import jimit as ji

from jimvc.models import Utils
from jimvc.models import Rules
from jimvc.models import IPPool

from base import Base


__author__ = 'James Iter'
__date__ = '2018-12-15'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_ip_pool',
    __name__,
    url_prefix='/api/ip_pool'
)

blueprints = Blueprint(
    'api_ip_pools',
    __name__,
    url_prefix='/api/ip_pools'
)


ip_pool_base = Base(the_class=IPPool, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.START_IP.value,
        Rules.END_IP.value,
        Rules.NETMASK.value,
        Rules.GATEWAY.value,
        Rules.DNS1.value,
        Rules.DNS2.value,
        Rules.ACTIVITY.value,
        Rules.NAME.value,
        Rules.DESCRIPTION.value
    ]

    ip_pool = IPPool()
    ip_pool.start_ip = request.json.get('start_ip')
    ip_pool.end_ip = request.json.get('end_ip')
    ip_pool.netmask = request.json.get('netmask')
    ip_pool.gateway = request.json.get('gateway')
    ip_pool.dns1 = request.json.get('dns1')
    ip_pool.dns2 = request.json.get('dns2')
    ip_pool.activity = request.json.get('activity')
    ip_pool.name = request.json.get('name', '')
    ip_pool.description = request.json.get('description', '')

    try:
        ji.Check.previewing(args_rules, ip_pool.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ip_pool.check_ip()

        if ip_pool.activity:
            # 如果新创建或被更新的 IP 池为活跃状态，则更新其它 IP 池为非活跃状态
            IPPool.update_by_filter({'activity': 0}, filter_str='id:gt:0')

        ip_pool.create()

        ip_pool.get()
        ret['data'] = ip_pool.__dict__
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

    if 'start_ip' in request.json:
        args_rules.append(
            Rules.START_IP.value,
        )

    if 'end_ip' in request.json:
        args_rules.append(
            Rules.END_IP.value,
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

    if 'activity' in request.json:
        args_rules.append(
            Rules.ACTIVITY.value,
        )

    if 'name' in request.json:
        args_rules.append(
            Rules.NAME.value,
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

        ip_pool = IPPool()

        # 检测所指定的 UUDIs 磁盘都存在
        for _id in ids.split(','):
            ip_pool.id = _id
            ip_pool.get()

        for _id in ids.split(','):
            ip_pool.id = _id
            ip_pool.get()
            ip_pool.start_ip = request.json.get('start_ip', ip_pool.start_ip)
            ip_pool.end_ip = request.json.get('end_ip', ip_pool.end_ip)
            ip_pool.netmask = request.json.get('netmask', ip_pool.netmask)
            ip_pool.gateway = request.json.get('gateway', ip_pool.gateway)
            ip_pool.dns1 = request.json.get('dns1', ip_pool.dns1)
            ip_pool.dns2 = request.json.get('dns2', ip_pool.dns2)
            ip_pool.activity = request.json.get('activity', ip_pool.activity)
            ip_pool.name = request.json.get('name', ip_pool.name)
            ip_pool.description = request.json.get('description', ip_pool.description)

            ip_pool.check_ip()

            if ip_pool.activity:
                # 如果新创建或被更新的 IP 池为活跃状态，则更新其它 IP 池为非活跃状态
                IPPool.update_by_filter({'activity': 0}, filter_str='id:gt:0')

            ip_pool.update()
            ip_pool.get()

            ret['data'].append(ip_pool.__dict__)

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_activity(_id):

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = list()

    args_rules = [
        Rules.ID.value
    ]

    if args_rules.__len__() < 1:
        return ret

    try:
        ji.Check.previewing(args_rules, {'id': _id})

        ip_pool = IPPool()
        ip_pool.id = _id
        ip_pool.get()

        ip_pool.activity = 1

        # 如果新创建或被更新的 IP 池为活跃状态，则更新其它 IP 池为非活跃状态
        IPPool.update_by_filter({'activity': 0}, filter_str='id:gt:0')

        ip_pool.update()
        ip_pool.get()

        ret['data'].append(ip_pool.__dict__)

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(ids):
    return ip_pool_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return ip_pool_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return ip_pool_base.content_search()


@Utils.dumps2response
def r_delete(ids):
    return ip_pool_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')

