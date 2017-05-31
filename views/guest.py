#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from flask import Blueprint, render_template, url_for, request
import requests


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'v_guest',
    __name__,
    url_prefix='/guest'
)

blueprints = Blueprint(
    'v_guests',
    __name__,
    url_prefix='/guests'
)


def show():
    host_url = request.host_url.rstrip('/')
    url = host_url + url_for('api_guests.r_get_by_filter')
    ret = requests.get(url=url)
    ret = json.loads(ret.content)
    return render_template('guest.html', data=ret['data'])


