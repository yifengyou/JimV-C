#!/usr/bin/env python
# -*- coding: utf-8 -*-


from math import ceil

import requests
from flask import Blueprint, url_for
from flask import request
from werkzeug.datastructures import ImmutableMultiDict
import json
import jimit as ji

from jimvc.api.base import Base
from jimvc.models import SSHKey, OSTemplateImage, OSTemplateProfile, GuestState
from jimvc.models import SSHKeyGuestMapping
from jimvc.models import Guest
from jimvc.models import Utils
from jimvc.models import Rules


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


def update_ssh_key(uuid):

    guest = Guest()
    guest.uuid = uuid
    guest.get_by('uuid')

    # 不支持更新离线虚拟机的 SSH-KEY
    if guest.status != GuestState.running.value:
        return

    os_template_image = OSTemplateImage()
    os_template_profile = OSTemplateProfile()

    os_template_image.id = guest.os_template_image_id
    os_template_image.get()

    os_template_profile.id = os_template_image.os_template_profile_id
    os_template_profile.get()

    # 不支持更新 Windows 虚拟机的 SSH-KEY
    if os_template_profile.os_type == 'windows':
        return

    rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['guest_uuid', 'eq', uuid]))

    ssh_keys_id = list()
    for row in rows:
        ssh_keys_id.append(row['ssh_key_id'].__str__())

    ssh_keys = list()

    if ssh_keys_id.__len__() > 0:
        rows, _ = SSHKey.get_by_filter(filter_str=':'.join(['id', 'in', ','.join(ssh_keys_id)]))
        for row in rows:
            ssh_keys.append(row['public_key'])

    else:
        ssh_keys.append('')

    message = {
        '_object': 'guest',
        'uuid': uuid,
        'node_id': guest.node_id,
        'action': 'update_ssh_key',
        'ssh_keys': ssh_keys,
        'os_type': os_template_profile.os_type,
        'passback_parameters': {'uuid': uuid, 'ssh_keys': ssh_keys, 'os_type': os_template_profile.os_type}
    }

    Utils.emit_instruction(message=json.dumps(message, ensure_ascii=False))


@Utils.dumps2response
def r_delete(ids):
    rows, _ = SSHKeyGuestMapping.get_by_filter(filter_str=':'.join(['ssh_key_id', 'in', ids]))
    SSHKeyGuestMapping.delete_by_filter(filter_str=':'.join(['ssh_key_id', 'in', ids]))

    for row in rows:
        update_ssh_key(uuid=row['guest_uuid'])

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
            ('filter', ':'.join(['uuid', 'notin', ','.join(guests_uuid)]) + ';' +
             ':'.join(['status', 'eq', str(GuestState.running.value)])),
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

            update_ssh_key(uuid=uuid)

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

                update_ssh_key(uuid=row['guest_uuid'])

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
def r_show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', None)

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    if order_by is not None:
        args.append('order_by=' + order_by)

    if order is not None:
        args.append('order=' + order)

    ssh_keys_url = url_for('api_ssh_keys.r_get_by_filter', _external=True)
    if keyword is not None:
        ssh_keys_url = url_for('api_ssh_keys.r_content_search', _external=True)

    if args.__len__() > 0:
        ssh_keys_url = ssh_keys_url + '?' + '&'.join(args)

    ssh_keys_ret = requests.get(url=ssh_keys_url, cookies=request.cookies)
    ssh_keys_ret = json.loads(ssh_keys_ret.content)

    last_page = int(ceil(ssh_keys_ret['paging']['total'] / float(page_size)))
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
        'ssh_keys': ssh_keys_ret['data'],
        'paging': ssh_keys_ret['paging'],
        'page': page,
        'page_size': page_size,
        'keyword': keyword,
        'pages': pages,
        'last_page': last_page,
        'order_by': order_by,
        'order': order
    }

    return ret


