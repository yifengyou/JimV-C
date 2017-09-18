#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, request, g, make_response
from flask import request
from flask import session
import json
import jimit as ji

from api.base import Base
from models import User
from models import Utils
from models import Rules


__author__ = 'James Iter'
__date__ = '2017/9/14'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_user',
    __name__,
    url_prefix='/api/user'
)

blueprints = Blueprint(
    'api_users',
    __name__,
    url_prefix='/api/users'
)


user_base = Base(the_class=User, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_sign_in():

    args_rules = [
        Rules.LOGIN_NAME.value,
        Rules.PASSWORD.value
    ]

    user = User()
    user.login_name = request.json.get('login_name')
    user.password = request.json.get('password')

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        plain_password = user.password
        user.get_by('login_name')

        if not ji.Security.ji_pbkdf2_check(password=plain_password, password_hash=user.password):
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40101)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 鉴权失败'])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        token = Utils.generate_token(user.id)
        session['token'] = token
        rep = make_response()
        rep.data = json.dumps({'state': ji.Common.exchange_state(20000)}, ensure_ascii=False)
        return rep

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_out():
    for key in session.keys():
        session.pop(key=key)


@Utils.dumps2response
def r_change_password():

    args_rules = [
        Rules.ID.value
    ]

    user = User()
    user.id = g.token.get('uid', 0).__str__()

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        user.get()

        old_password = request.json.get('old_password', '')

        if not ji.Security.ji_pbkdf2_check(password=old_password, password_hash=user.password):
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40101)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 鉴权失败'])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        args_rules = [
            Rules.PASSWORD.value
        ]

        user.password = request.json.get('password')

        ji.Check.previewing(args_rules, user.__dict__)
        user.password = ji.Security.ji_pbkdf2(user.password)
        user.update()
    except ji.PreviewingError, e:
        return json.loads(e.message)

