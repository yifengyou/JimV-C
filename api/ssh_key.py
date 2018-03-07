#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
from werkzeug.datastructures import ImmutableMultiDict
import json
import jimit as ji

from api.base import Base
from models import SSHKey
from models import SSHKeyGuestMapping
from models import Guest
from models import Utils
from models import Rules


__author__ = 'James Iter'
__date__ = '2018/2/26'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_ssh_key',
    __name__,
    url_prefix='/api/ssh_key'
)

blueprints = Blueprint(
    'api_ssh_keys',
    __name__,
    url_prefix='/api/ssh_keys'
)


ssh_key_base = Base(the_class=SSHKey, the_blueprint=blueprint, the_blueprints=blueprints)
guest_base = Base(the_class=Guest, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    args_rules = [
        Rules.LABEL.value,
        Rules.PUBLIC_KEY.value
    ]

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ji.Check.previewing(args_rules, request.json)

        ssh_key = SSHKey()

        ssh_key.label = request.json.get('label')
        ssh_key.public_key = request.json.get('public_key')

        if ssh_key.exist_by('public_key'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', ssh_key.public_key])
            return ret

        ssh_key.create()

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    ssh_key = SSHKey()

    args_rules = [
        Rules.ID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if 'public_key' in request.json:
        args_rules.append(
            Rules.PUBLIC_KEY.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        ssh_key.id = request.json.get('id')

        ssh_key.get()
        ssh_key.label = request.json.get('label', ssh_key.label)
        ssh_key.public_key = request.json.get('public_key', ssh_key.public_key)

        ssh_key.update()
        ssh_key.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = ssh_key.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(ids):
    return ssh_key_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return ssh_key_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return ssh_key_base.content_search()


@Utils.dumps2response
def r_delete(ids):
    # TODO: 做好依赖逻辑处理。比如已关联 ssh_key 的删除。
    return ssh_key_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_bound(ssh_key_id):

    args_rules = [
        Rules.SSH_KEY_ID_EXT.value,
    ]

    try:
        ji.Check.previewing(args_rules, {'ssh_key_id': ssh_key_id})

        rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'eq', ssh_key_id]))
        guests_uuid = list()
        for row in rows:
            guests_uuid.append(row['guest_uuid'])

        if guests_uuid.__len__() == 0:
            guests_uuid.append('_')

        request.__setattr__('args', ImmutableMultiDict([
            ('filter', ':'.join(['uuid', 'in', ','.join(guests_uuid)])),
            ('page_size', 10000)
        ]))

        return guest_base.get_by_filter()
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_unbound(ssh_key_id):

    args_rules = [
        Rules.SSH_KEY_ID_EXT.value,
    ]

    try:
        ji.Check.previewing(args_rules, {'ssh_key_id': ssh_key_id})

        rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'eq', ssh_key_id]))
        guests_uuid = list()
        for row in rows:
            guests_uuid.append(row['guest_uuid'])

        if guests_uuid.__len__() == 0:
            guests_uuid.append('_')

        request.__setattr__('args', ImmutableMultiDict([
            ('filter', ':'.join(['uuid', 'notin', ','.join(guests_uuid)])),
            ('page_size', 10000)
        ]))

        return guest_base.get_by_filter()
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_bind(ssh_key_id, uuids):

    args_rules = [
        Rules.SSH_KEY_ID_EXT.value,
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'ssh_key_id': ssh_key_id, 'uuids': uuids})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        ssh_key = SSHKey()
        ssh_key.id = ssh_key_id

        # 判断 ssh_key id 为 ssh_key_id 的对象是否存在
        if not ssh_key.exist():
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ssh_key_id: ', ssh_key_id])
            return ret

        # 获取已经和该 ssh_key 绑定过的 guest uuid 集合，用于判断是否已经绑定过该 ssh_key，避免重复绑定
        rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'eq', ssh_key_id]))

        guests_uuid = list()
        for row in rows:
            guests_uuid.append(row['guest_uuid'])

        ssh_key_guest_mapping = SSHKeyGuestMapping()
        for uuid in uuids.split(','):
            # 如果已经绑定过，则忽略
            if uuid in guests_uuid:
                continue

            ssh_key_guest_mapping.ssh_key_id = ssh_key_id
            ssh_key_guest_mapping.guest_uuid = uuid
            ssh_key_guest_mapping.create()

        # 返回执行结果
        rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'eq', ssh_key_id]))
        guests_uuid = list()
        for row in rows:
            guests_uuid.append(row['guest_uuid'])

        if guests_uuid.__len__() == 0:
            guests_uuid.append('_')

        request.__setattr__('args', ImmutableMultiDict([
            ('filter', ':'.join(['uuid', 'in', ','.join(guests_uuid)])),
            ('page_size', 10000)
        ]))

        return guest_base.get_by_filter()
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_unbind(ssh_key_id, uuids):

    args_rules = [
        Rules.SSH_KEY_ID_EXT.value,
        Rules.UUIDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {'ssh_key_id': ssh_key_id, 'uuids': uuids})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        # 获取已经和该 ssh_key 绑定过的映射集合，从中获取映射 id，用于解绑操作
        rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'eq', ssh_key_id]))

        guests_uuid = uuids.split(',')

        ssh_key_guest_mapping = SSHKeyGuestMapping()
        for row in rows:
            # 解除已经绑定过的 guest
            if row['guest_uuid'] in guests_uuid:
                ssh_key_guest_mapping.id = row['id']
                ssh_key_guest_mapping.delete()

        # 返回执行结果
        rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'eq', ssh_key_id]))
        guests_uuid = list()
        for row in rows:
            guests_uuid.append(row['guest_uuid'])

        if guests_uuid.__len__() == 0:
            guests_uuid.append('_')

        request.__setattr__('args', ImmutableMultiDict([
            ('filter', ':'.join(['uuid', 'in', ','.join(guests_uuid)])),
            ('page_size', 10000)
        ]))

        return guest_base.get_by_filter()
    except ji.PreviewingError, e:
        return json.loads(e.message)

