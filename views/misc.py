#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
from flask import Blueprint, render_template, request


__author__ = 'James Iter'
__date__ = '2017/9/12'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_misc',
    __name__,
    url_prefix='/'
)


def login():
    return render_template('login.html')


def change_password():
    return render_template('change_password.html')


def recover_password():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        login_name = request.form.get('login_name')

        url = host_url + '/api/user/_send_reset_password_email/' + login_name

        r = requests.put(url)
        j_r = json.loads(r.content)

        return render_template('success.html',
                               go_back_url='/login',
                               timeout=10000, title=u'提交成功',
                               message_title=u'恢复密码的请求已被接受',
                               message=u'恢复密码的URL已发送至您的邮箱，请查看您预留的邮箱：' + j_r['data']['email'] + u'。页面将在10秒钟后自动跳转到登录页面！')

    else:
        return render_template('recover_password.html')


def reset_password():
    return render_template('reset_password.html')

