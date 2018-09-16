#!/usr/bin/env python
# -*- coding: utf-8 -*-


from math import ceil

import requests
from flask import Blueprint, url_for
from flask import request
import jimit as ji
import json

from api.base import Base
from models import OSTemplateImage, OSTemplateProfile, Host, Config, OSTemplateImageKind, Guest
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_os_template_image',
    __name__,
    url_prefix='/api/os_template_image'
)

blueprints = Blueprint(
    'api_os_templates_image',
    __name__,
    url_prefix='/api/os_templates_image'
)


os_template_image_base = Base(the_class=OSTemplateImage, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_template_image = OSTemplateImage()

    args_rules = [
        Rules.LABEL.value,
        Rules.DESCRIPTION.value,
        Rules.PATH.value,
        Rules.LOGO.value,
        Rules.OS_TEMPLATE_PROFILE_ID_EXT.value,
        Rules.ACTIVE.value,
        Rules.OS_TEMPLATE_IMAGE_KIND.value
    ]

    os_template_image.label = request.json.get('label')
    os_template_image.description = request.json.get('description')
    os_template_image.path = request.json.get('path')
    os_template_image.logo = request.json.get('logo')
    os_template_image.active = bool(int(request.json.get('active', 1)))
    os_template_image.os_template_profile_id = request.json.get('os_template_profile_id')
    os_template_image.kind = request.json.get('kind')
    os_template_image.progress = 100

    try:
        ji.Check.previewing(args_rules, os_template_image.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if os_template_image.exist_by('path'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template_image.path])
            return ret

        os_template_profile = OSTemplateProfile()
        os_template_profile.id = os_template_image.os_template_profile_id
        if not os_template_profile.exist():
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 操作系统模板描述文件ID: ',
                                                    os_template_image.os_template_profile_id.__str__()])
            return ret

        os_template_image.create()
        os_template_image.get_by('path')
        ret['data'] = os_template_image.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_template_image = OSTemplateImage()

    args_rules = [
        Rules.ID.value
    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if 'description' in request.json:
        args_rules.append(
            Rules.DESCRIPTION.value,
        )

    if 'path' in request.json:
        args_rules.append(
            Rules.PATH.value,
        )

    if 'active' in request.json:
        args_rules.append(
            Rules.ACTIVE.value,
        )

    if 'logo' in request.json:
        args_rules.append(
            Rules.LOGO.value,
        )

    if 'os_template_profile_id' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_PROFILE_ID_EXT.value,
        )

    if 'kind' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_IMAGE_KIND.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_template_image.id = request.json.get('id')

        os_template_image.get()
        os_template_image.label = request.json.get('label', os_template_image.label)
        os_template_image.description = request.json.get('description', os_template_image.description)
        os_template_image.path = request.json.get('path', os_template_image.path)
        os_template_image.active = request.json.get('active', os_template_image.active)
        os_template_image.logo = request.json.get('logo', os_template_image.logo)
        os_template_image.os_template_profile_id = \
            request.json.get('os_template_profile_id', os_template_image.os_template_profile_id)
        os_template_image.kind = request.json.get('kind', os_template_image.kind)

        os_template_image.update()
        os_template_image.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_template_image.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)

    config = Config()
    config.id = 1
    config.get()

    # 取全部活着的 hosts
    available_hosts = Host.get_available_hosts(nonrandom=None)

    if available_hosts.__len__() == 0:
        ret['state'] = ji.Common.exchange_state(50351)
        return ret

    chosen_host = available_hosts[0]
    node_id = chosen_host['node_id']

    os_template_image = OSTemplateImage()

    # TODO: 加入对，是否有被 Guest 引用的判断
    for _id in ids.split(','):
        os_template_image.id = _id
        os_template_image.get()

    for _id in ids.split(','):
        os_template_image.id = _id
        os_template_image.get()

        # 暂时不支持从计算节点上，删除公共镜像
        if os_template_image.kind == OSTemplateImageKind.public.value:
            os_template_image.delete()
            continue

        elif os_template_image.kind == OSTemplateImageKind.custom.value:
            os_template_image.progress = 254

            message = {
                '_object': 'os_template_image',
                'action': 'delete',
                'storage_mode': config.storage_mode,
                'dfs_volume': config.dfs_volume,
                'template_path': os_template_image.path,
                # uuid 这里没有实际意义，仅仅是为了迁就 JimV-C 的个命令格式
                'uuid': None,
                'node_id': node_id,
                'os_template_image_id': os_template_image.id,
                'passback_parameters': {'id': os_template_image.id}
            }

            Utils.emit_instruction(message=json.dumps(message))

            os_template_image.update()

    return ret


@Utils.dumps2response
def r_get(ids):
    return os_template_image_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    ret = os_template_image_base.get_by_filter()

    if '200' != ret['state']['code']:
        return ret

    os_template_images_id = list()

    for os_template_image in ret['data']:
        os_template_image_id = os_template_image['id']

        if os_template_image_id not in os_template_images_id:
            os_template_images_id.append(os_template_image_id)

    rows, _ = Guest.get_by_filter(filter_str=':'.join(['os_template_image_id', 'in',
                                                       ','.join(_id.__str__() for _id in os_template_images_id)]))

    os_template_image_guest_mapping = dict()

    for guest in rows:
        os_template_image_id = guest['os_template_image_id']

        if os_template_image_id not in os_template_image_guest_mapping:
            os_template_image_guest_mapping[os_template_image_id] = list()

        os_template_image_guest_mapping[os_template_image_id].append(guest)

    for i, os_template_image in enumerate(ret['data']):

        if os_template_image['id'] in os_template_image_guest_mapping:
            ret['data'][i]['guests'] = os_template_image_guest_mapping[os_template_image['id']]

    return ret


@Utils.dumps2response
def r_content_search():
    ret = os_template_image_base.content_search()

    if '200' != ret['state']['code']:
        return ret

    os_template_images_id = list()

    for os_template_image in ret['data']:
        os_template_image_id = os_template_image['id']

        if os_template_image_id not in os_template_images_id:
            os_template_images_id.append(os_template_image_id)

    rows, _ = Guest.get_by_filter(filter_str=':'.join(['os_template_image_id', 'in',
                                                       ','.join(_id.__str__() for _id in os_template_images_id)]))

    os_template_image_guest_mapping = dict()

    for guest in rows:
        os_template_image_id = guest['os_template_image_id']

        if os_template_image_id not in os_template_image_guest_mapping:
            os_template_image_guest_mapping[os_template_image_id] = list()

        os_template_image_guest_mapping[os_template_image_id].append(guest)

    for i, os_template_image in enumerate(ret['data']):

        if os_template_image['id'] in os_template_image_guest_mapping:
            ret['data'][i]['guests'] = os_template_image_guest_mapping[os_template_image['id']]

    return ret


@Utils.dumps2response
def r_show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 1000))
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

    os_templates_image_url = url_for('api_os_templates_image.r_get_by_filter', _external=True)
    if keyword is not None:
        os_templates_image_url = url_for('api_os_templates_image.r_content_search', _external=True)

    if args.__len__() > 0:
        os_templates_image_url = os_templates_image_url + '?' + '&'.join(args)

    os_templates_image_ret = requests.get(url=os_templates_image_url, cookies=request.cookies)
    os_templates_image_ret = json.loads(os_templates_image_ret.content)

    public_count = 0
    custom_count = 0

    for os_template_image in os_templates_image_ret['data']:
        if os_template_image['kind'] == 0:
            public_count += 1

        elif os_template_image['kind'] == 1:
            custom_count += 1

    os_templates_profile, _ = OSTemplateProfile.get_by_filter()

    os_templates_profile_mapping_by_id = dict()
    for os_template_profile in os_templates_profile:
        os_templates_profile_mapping_by_id[os_template_profile['id']] = os_template_profile

    last_page = int(ceil(os_templates_image_ret['paging']['total'] / float(page_size)))
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
        'os_templates_image': os_templates_image_ret['data'],
        'os_templates_profile_mapping_by_id': os_templates_profile_mapping_by_id,
        'page': page,
        'page_size': page_size,
        'keyword': keyword,
        'pages': pages,
        'last_page': last_page,
        'order_by': order_by,
        'order': order,
        'public_count': public_count,
        'custom_count': custom_count
    }

    return ret

