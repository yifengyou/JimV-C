#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request, abort, url_for
import requests
from . import render


__author__ = 'James Iter'
__date__ = '2017/8/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_config',
    __name__,
    url_prefix='/config'
)


def show():
    config_url = url_for('api_config.r_get', _external=True)
    config_ret = requests.get(url=config_url, cookies=request.cookies)
    config_ret = json.loads(config_ret.content)

    # 检测 JimV 的配置是否已被初始化，只有未被初始化时，才展现初始化配置页面
    if config_ret['state']['code'] == '404':
        abort(404)

    return render('config_show.html', config=config_ret['data'])


def create():
    config_url = url_for('api_config.r_get', _external=True)
    config_ret = requests.get(url=config_url, cookies=request.cookies)
    config_ret = json.loads(config_ret.content)

    # 检测 JimV 的配置是否已被初始化，只有未被初始化时，才展现初始化配置页面
    if config_ret['state']['code'] == '404':
        return render('config_init.html')
    else:
        abort(404)

