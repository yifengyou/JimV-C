#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from api.base import Base
from models import OSTemplateImage, OSTemplateProfile
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
        Rules.ACTIVE.value
    ]

    os_template_image.label = request.json.get('label')
    os_template_image.description = request.json.get('description')
    os_template_image.path = request.json.get('path')
    os_template_image.logo = request.json.get('logo')
    os_template_image.active = bool(int(request.json.get('active', 1)))
    os_template_image.os_template_profile_id = request.json.get('os_template_profile_id')

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
    return os_template_image_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_template_image_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_template_image_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_template_image_base.content_search()

