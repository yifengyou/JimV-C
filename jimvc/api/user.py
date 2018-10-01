#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint, g, make_response
from flask import request
from flask import session
import json
import jimit as ji

from jimvc.api.base import Base
from jimvc.models import app_config
from jimvc.models import User
from jimvc.models import Utils
from jimvc.models import Rules


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


@Utils.dumps2response
def r_reset_password(token):

    args_rules = [
        Rules.TOKEN.value
    ]

    try:
        ji.Check.previewing(args_rules, {'token': token})

        token = Utils.verify_token(token, audience='r_reset_password')

        user = User()
        user.id = token['uid']
        user.get()

        args_rules = [
            Rules.PASSWORD.value
        ]

        user.password = request.json.get('password')

        ji.Check.previewing(args_rules, user.__dict__)
        user.password = ji.Security.ji_pbkdf2(user.password)
        user.update()
    except (ji.PreviewingError, ji.JITError), e:
        return json.loads(e.message)


@Utils.dumps2response
def r_send_reset_password_email(login_name):

    args_rules = [
        Rules.LOGIN_NAME.value
    ]

    try:
        ji.Check.previewing(args_rules, {'login_name': login_name})

        user = User()
        try:
            user.login_name = login_name
            user.get_by('login_name')

        except ji.PreviewingError, e:
            # 如果 login_name 没有找到，则尝试从email里面查找
            # 因为用户可能会把登录名理解成email
            user.email = login_name
            user.get_by('email')

        host_url = request.host_url.rstrip('/')
        # 5 分钟有效期
        token = Utils.generate_token(uid=user.id, ttl=300, audience='r_reset_password')

        reset_password_url = '/'.join([host_url, 'reset_password', token])

        smtp_server = ji.NetUtils.smtp_init(host=app_config['smtp_host'], port=app_config.get('smtp_port', None),
                                            login_name=app_config['smtp_user'], password=app_config['smtp_password'],
                                            tls=app_config['smtp_starttls'])

        ji.NetUtils.send_mail(smtp_server=smtp_server, sender=app_config['smtp_user'],
                              receivers=[user.email], title=u'重置登录密码',
                              message=u'请复制以下地址到浏览器中打开：' + reset_password_url)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = {'email': user.email}

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

