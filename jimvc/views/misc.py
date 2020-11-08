#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
from flask import Blueprint, request

from . import render


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
    return render('login.html')


def change_password():
    return render('change_password.html')


def recover_password():
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        login_name = request.form.get('login_name')

        url = host_url + '/api/user/_send_reset_password_email/' + login_name

        r = requests.put(url)
        j_r = json.loads(r.content)

        return render('success.html',
                      go_back_url='/login',
                      timeout=10000, title='提交成功',
                      message_title='恢复密码的请求已被接受',
                      message='恢复密码的URL已发送至您的邮箱，请查看您预留的邮箱：' + j_r['data']['email'] + '。页面将在10秒钟后自动跳转到登录页面！')

    else:
        return render('recover_password.html')


def reset_password(token):
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        password = request.form.get('password')

        payload = {
            "password": password
        }
        url = host_url + '/api/user/_reset_password/' + token

        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        j_r = json.loads(r.content)

        if j_r['state']['code'] == '200':
            return render('success.html',
                          go_back_url='/login',
                          timeout=10000, title='提交成功',
                          message_title='重置密码成功',
                          message='页面将在10秒钟后自动跳转到登录页面！')

        else:
            return render('failure.html',
                          go_back_url='/login',
                          timeout=10000, title='提交失败',
                          message_title='重置密码失败',
                          message=j_r['state']['sub']['zh-cn'] + '，页面将在10秒钟后自动跳转到登录页面！')

    else:
        return render('reset_password.html', token=token)


def about():
    return render('about.html')

