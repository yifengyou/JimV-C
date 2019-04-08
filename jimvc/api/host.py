#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json

import requests
from flask import Blueprint, request, url_for
import jimit as ji

from jimvc.models import app_config, Guest
from jimvc.models import Database as db
from jimvc.models import Utils, Rules, Host
from jimvc.models import GuestState


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_host',
    __name__,
    url_prefix='/api/host'
)

blueprints = Blueprint(
    'api_hosts',
    __name__,
    url_prefix='/api/hosts'
)


@Utils.dumps2response
def r_nonrandom(hosts_name, random):

    args_rules = [
        Rules.HOSTS_NAME.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: hosts_name})

        if str(random).lower() in ['false', '0']:
            random = False

        else:
            random = True

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        Host.set_allocation_mode(hosts_name=hosts_name.split(','), random=random)

        ret['data'] = Host.get_all()
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(nodes_id):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: nodes_id})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        if -1 == nodes_id.find(','):
            node_id = nodes_id
            if db.r.hexists(app_config['hosts_info'], node_id):
                v = json.loads(db.r.hget(app_config['hosts_info'], node_id))
                v = Host.alive_check(v)
                v['node_id'] = node_id
                ret['data'] = v

        else:
            for node_id in nodes_id.split(','):
                if db.r.hexists(app_config['hosts_info'], node_id):
                    v = json.loads(db.r.hget(app_config['hosts_info'], node_id))
                    v = Host.alive_check(v)
                    v['node_id'] = node_id
                    ret['data'].append(v)

            if ret['data'].__len__() > 1:
                ret['data'].sort(key=lambda _k: _k['boot_time'])

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get_by_filter():

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        alive = None

        if 'alive' in request.args:
            alive = request.args['alive']

            if str(alive).lower() in ['false', '0']:
                alive = False

            else:
                alive = True

        for host in Host.get_all():
            if alive is not None and alive is not host['alive']:
                continue

            ret['data'].append(host)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_content_search():
    keyword = request.args.get('keyword', '')

    args_rules = [
        Rules.KEYWORD.value
    ]

    try:
        ji.Check.previewing(args_rules, {'keyword': keyword})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        for host in Host.get_all():
            if -1 != host['hostname'].lower().find(keyword.lower()):
                ret['data'].append(host)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(nodes_id):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: nodes_id})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        if -1 == nodes_id.find(','):
            node_id = nodes_id
            if db.r.hexists(app_config['hosts_info'], node_id):
                v = json.loads(db.r.hget(app_config['hosts_info'], node_id))
                v['node_id'] = node_id
                ret['data'] = v
                db.r.hdel(app_config['hosts_info'], node_id)

        else:
            for node_id in nodes_id.split(','):
                if db.r.hexists(app_config['hosts_info'], node_id):
                    v = json.loads(db.r.hget(app_config['hosts_info'], node_id))
                    v['node_id'] = node_id
                    ret['data'].append(v)
                    db.r.hdel(app_config['hosts_info'], node_id)

            if ret['data'].__len__() > 1:
                ret['data'].sort(key=lambda _k: _k['boot_time'])

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 100))
    keyword = request.args.get('keyword', None)

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    hosts_url = url_for('api_hosts.r_get_by_filter', _external=True)
    if keyword is not None:
        hosts_url = url_for('api_hosts.r_content_search', _external=True)

    if args.__len__() > 0:
        hosts_url = hosts_url + '?' + '&'.join(args)

    hosts_ret = requests.get(url=hosts_url, cookies=request.cookies, verify=False)
    hosts_ret = json.loads(hosts_ret.content)

    node_id_amd_state_with_guests_count = dict()
    rows, _ = Guest.get_all()

    for i, host in enumerate(hosts_ret['data']):
        hosts_ret['data'][i]['analysis'] = {
            'all_instance': 0,
            'running_instance': 0,
            'all_vcpu': 0,
            'using_vcpu': 0,
            'all_memory': 0,
            'using_memory': 0
        }

    for row in rows:
        node_id = row['node_id'].__str__()
        if node_id not in node_id_amd_state_with_guests_count:
            node_id_amd_state_with_guests_count[node_id] = {
                'all_instance': 0,
                'running_instance': 0,
                'all_vcpu': 0,
                'using_vcpu': 0,
                'all_memory': 0,
                'using_memory': 0
            }

        node_id_amd_state_with_guests_count[node_id]['all_instance'] += 1
        node_id_amd_state_with_guests_count[node_id]['all_vcpu'] += row['cpu']
        node_id_amd_state_with_guests_count[node_id]['all_memory'] += row['memory']

        if row['status'] in [GuestState.running.value, GuestState.booting.value, GuestState.migrating.value]:
            node_id_amd_state_with_guests_count[node_id]['running_instance'] += 1
            node_id_amd_state_with_guests_count[node_id]['using_vcpu'] += row['cpu']
            node_id_amd_state_with_guests_count[node_id]['using_memory'] += row['memory']

    for i, host in enumerate(hosts_ret['data']):
        if host['node_id'] in node_id_amd_state_with_guests_count:
            hosts_ret['data'][i]['analysis'] = node_id_amd_state_with_guests_count[host['node_id']]

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    ret['data'] = {
        'hosts': hosts_ret['data'],
        'keyword': keyword
    }

    return ret


