#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from flask import Blueprint, render_template, url_for, request
import requests
from math import ceil


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
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    host_url = request.host_url.rstrip('/')

    guests_url = host_url + url_for('api_guests.r_get_by_filter')
    if keyword is not None:
        guests_url = host_url + url_for('api_guests.r_content_search')

    os_template_url = host_url + url_for('api_os_templates.r_get_by_filter')

    if args.__len__() > 0:
        guests_url = guests_url + '?' + '&'.join(args)

    guests_ret = requests.get(url=guests_url)
    guests_ret = json.loads(guests_ret.content)

    os_template_ret = requests.get(url=os_template_url)
    os_template_ret = json.loads(os_template_ret.content)
    os_template_mapping_by_id = dict()
    for os_template in os_template_ret['data']:
        os_template_mapping_by_id[os_template['id']] = os_template

    last_page = int(ceil(guests_ret['paging']['total'] / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page:
                break

    return render_template('guest_show.html', guests_ret=guests_ret,
                           os_template_mapping_by_id=os_template_mapping_by_id, page=page,
                           page_size=page_size, keyword=keyword, pages=pages, last_page=last_page)


def create():
    host_url = request.host_url.rstrip('/')
    os_template_url = host_url + url_for('api_os_templates.r_get_by_filter')
    os_template_ret = requests.get(url=os_template_url)
    os_template_ret = json.loads(os_template_ret.content)

    return render_template('guest_create.html', os_template_data=os_template_ret['data'])
