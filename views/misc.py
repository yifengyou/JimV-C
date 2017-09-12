#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request
import requests


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
    host_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        payload = {
            'jimv_edition': int(request.form.get('jimv_edition', 0))
        }

        url = host_url + '/api/config'
        headers = {'content-type': 'application/json'}
        config_ret = requests.post(url, data=json.dumps(payload), headers=headers)
        config_ret = json.loads(config_ret.content)
        return render_template('success.html', go_back_url='/', timeout=5000, title='提交成功',
                               message_title='初始化 JimV 请求已被接受',
                               message='JimV 已被初始化。页面将在5秒钟后自动跳转到实例列表页面！')

    else:
        return render_template('login.html')

