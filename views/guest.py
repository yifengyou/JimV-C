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
    guests_url = host_url + url_for('api_guests.r_get_by_filter')
    os_template_url = host_url + url_for('api_os_templates.r_get_by_filter')

    guests_ret = requests.get(url=guests_url)
    guests_ret = json.loads(guests_ret.content)

    os_template_ret = requests.get(url=os_template_url)
    os_template_ret = json.loads(os_template_ret.content)
    os_template_mapping_by_id = dict()
    for os_template in os_template_ret['data']:
        os_template_mapping_by_id[os_template['id']] = os_template

    return render_template('guest.html', guests_data=guests_ret['data'],
                           os_template_mapping_by_id=os_template_mapping_by_id)


