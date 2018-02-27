#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
import json
import jimit as ji

from api.base import Base
from models import SSHKey
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
    return ssh_key_base.delete(ids=ids, ids_rule=Rules.IDS.value, by_field='id')
