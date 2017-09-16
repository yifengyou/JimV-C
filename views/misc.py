#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, request
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
            'login_name': request.form.get('login_name'),
            'password': request.form.get('password')
        }

        url = host_url + '/api/user/_sign_in'
        headers = {'content-type': 'application/json'}
        ret = requests.post(url, data=json.dumps(payload), headers=headers, cookies=request.cookies)
        ret = json.loads(ret.content)

        if ret['state']['code'] == '200':
            return

        else:
            pass

    else:
        return render_template('login.html')

