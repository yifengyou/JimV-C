#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import jimit as ji
import json

from api.base import Base
from models import OSTemplateProfile
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2018/2/4'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_os_template_profile',
    __name__,
    url_prefix='/api/os_template_profile'
)

blueprints = Blueprint(
    'api_os_templates_profile',
    __name__,
    url_prefix='/api/os_templates_profile'
)


os_template_profile_base = Base(the_class=OSTemplateProfile, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_create():

    os_template_profile = OSTemplateProfile()

    args_rules = [
        Rules.LABEL.value,
        Rules.DESCRIBE.value,
        Rules.OS_TYPE.value,
        Rules.OS_DISTRO.value,
        Rules.OS_MAJOR.value,
        Rules.OS_MINOR.value,
        Rules.OS_ARCH.value,
        Rules.OS_PRODUCT_NAME.value,
        Rules.ACTIVE.value,
        Rules.ICON.value,
        Rules.OS_TEMPLATE_INITIALIZE_OPERATE_SET_ID_EXT.value
    ]

    os_template_profile.label = request.json.get('label')
    os_template_profile.describe = request.json.get('describe')
    os_template_profile.os_type = request.json.get('os_type')
    os_template_profile.os_distro = request.json.get('os_distro')
    os_template_profile.os_major = request.json.get('os_major')
    os_template_profile.os_minor = request.json.get('os_minor')
    os_template_profile.os_arch = request.json.get('os_arch')
    os_template_profile.os_product_name = request.json.get('os_product_name')
    os_template_profile.active = request.json.get('active')
    os_template_profile.icon = request.json.get('icon')
    os_template_profile.os_template_initialize_operate_set_id = \
        request.json.get('os_template_initialize_operate_set_id')

    try:
        ji.Check.previewing(args_rules, os_template_profile.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if os_template_profile.exist_by('label'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', os_template_profile.label])
            return ret

        os_template_profile.create()
        os_template_profile.get_by('label')
        ret['data'] = os_template_profile.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_update(_id):

    os_template_profile = OSTemplateProfile()

    args_rules = [
        Rules.ID.value

    ]

    if 'label' in request.json:
        args_rules.append(
            Rules.LABEL.value,
        )

    if 'describe' in request.json:
        args_rules.append(
            Rules.DESCRIBE.value,
        )

    if 'os_type' in request.json:
        args_rules.append(
            Rules.OS_TYPE.value,
        )

    if 'os_distro' in request.json:
        args_rules.append(
            Rules.OS_DISTRO.value,
        )

    if 'os_major' in request.json:
        args_rules.append(
            Rules.OS_MAJOR.value,
        )

    if 'os_minor' in request.json:
        args_rules.append(
            Rules.OS_MINOR.value,
        )

    if 'os_arch' in request.json:
        args_rules.append(
            Rules.OS_ARCH.value,
        )

    if 'os_product_name' in request.json:
        args_rules.append(
            Rules.OS_PRODUCT_NAME.value,
        )

    if 'active' in request.json:
        args_rules.append(
            Rules.ACTIVE.value,
        )

    if 'icon' in request.json:
        args_rules.append(
            Rules.ICON.value,
        )

    if 'os_template_initialize_operate_set_id' in request.json:
        args_rules.append(
            Rules.OS_TEMPLATE_INITIALIZE_OPERATE_SET_ID_EXT.value,
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        os_template_profile.id = request.json.get('id')

        os_template_profile.get()
        os_template_profile.label = request.json.get('label', os_template_profile.label)
        os_template_profile.describe = request.json.get('describe', os_template_profile.describe)
        os_template_profile.os_type = request.json.get('os_type', os_template_profile.os_type)
        os_template_profile.os_distro = request.json.get('os_distro', os_template_profile.os_distro)
        os_template_profile.os_major = request.json.get('os_major', os_template_profile.os_major)
        os_template_profile.os_minor = request.json.get('os_minor', os_template_profile.os_minor)
        os_template_profile.os_arch = request.json.get('os_arch', os_template_profile.os_arch)
        os_template_profile.os_product_name = request.json.get('os_product_name', os_template_profile.os_product_name)
        os_template_profile.active = request.json.get('active', os_template_profile.active)
        os_template_profile.icon = request.json.get('icon', os_template_profile.icon)
        os_template_profile.os_template_initialize_operate_set_id = request.json.get(
            'os_template_initialize_operate_set_id', os_template_profile.os_template_initialize_operate_set_id)

        os_template_profile.update()
        os_template_profile.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = os_template_profile.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(ids):
    return os_template_profile_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get(ids):
    return os_template_profile_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return os_template_profile_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return os_template_profile_base.content_search()

