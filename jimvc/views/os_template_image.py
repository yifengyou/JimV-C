#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, url_for, request
import requests
from . import render


__author__ = 'James Iter'
__date__ = '2018/2/5'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'v_os_template_image',
    __name__,
    url_prefix='/os_template_image'
)

blueprints = Blueprint(
    'v_os_templates_image',
    __name__,
    url_prefix='/os_templates_image'
)


def show():
    url = url_for('api_os_templates_image.r_show', _external=True)
    if request.args.__len__() >= 1:
        args = list()

        for k, v in list(request.args.items()):
            args.append('='.join([k, v]))

        url += '?' + '&'.join(args)

    ret = requests.get(url=url, cookies=request.cookies)
    ret = json.loads(ret.content)

    return render('os_templates_image_show.html', os_templates_image=ret['data']['os_templates_image'],
                  os_templates_profile_mapping_by_id=ret['data']['os_templates_profile_mapping_by_id'],
                  page=ret['data']['page'], page_size=ret['data']['page_size'], keyword=ret['data']['keyword'],
                  pages=ret['data']['pages'], order_by=ret['data']['order_by'], order=ret['data']['order'],
                  last_page=ret['data']['last_page'], public_count=ret['data']['public_count'],
                  custom_count=ret['data']['custom_count'])


