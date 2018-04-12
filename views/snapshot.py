#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, render_template, url_for, request, redirect
import requests
from math import ceil


__author__ = 'James Iter'
__date__ = '2018/3/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'v_snapshot',
    __name__,
    url_prefix='/snapshot'
)

blueprints = Blueprint(
    'v_snapshots',
    __name__,
    url_prefix='/snapshots'
)


def show():
    args = list()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', None)
    order = request.args.get('order', 'desc')

    if page is not None:
        args.append('page=' + page.__str__())

    if page_size is not None:
        args.append('page_size=' + page_size.__str__())

    if keyword is not None:
        args.append('keyword=' + keyword.__str__())

    if order_by is not None:
        args.append('order_by=' + order_by)

    if order is not None:
        args.append('order=' + order)

    host_url = request.host_url.rstrip('/')
    snapshots_url = host_url + url_for('api_snapshots.r_get_by_filter')
    if keyword is not None:
        snapshots_url = host_url + url_for('api_snapshots.r_content_search')

    if args.__len__() > 0:
        snapshots_url = snapshots_url + '?' + '&'.join(args)

    snapshots_ret = requests.get(url=snapshots_url, cookies=request.cookies)
    snapshots_ret = json.loads(snapshots_ret.content)

    guests_uuid = list()

    for snapshot in snapshots_ret['data']:
        guests_uuid.append(snapshot['guest_uuid'])

    guests_url = host_url + url_for('api_guests.r_get_by_filter', filter='uuid:in:' + ','.join(guests_uuid))

    guests_ret = requests.get(url=guests_url, cookies=request.cookies)
    guests_ret = json.loads(guests_ret.content)

    # Guest uuid 与 Guest 的映射
    guests_mapping_by_uuid = dict()
    for guest in guests_ret['data']:
        guests_mapping_by_uuid[guest['uuid']] = guest

    for i, snapshot in enumerate(snapshots_ret['data']):
        if snapshot['guest_uuid'].__len__() == 36:
            snapshots_ret['data'][i]['guest'] = guests_mapping_by_uuid[snapshot['guest_uuid']]

    last_page = int(ceil(1 / float(page_size)))
    page_length = 5
    pages = list()
    if page < int(ceil(page_length / 2.0)):
        for i in range(1, page_length + 1):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    elif last_page - page < page_length / 2:
        for i in range(last_page - page_length + 1, last_page + 1):
            if i < 1:
                continue
            pages.append(i)

    else:
        for i in range(page - page_length / 2, page + int(ceil(page_length / 2.0))):
            pages.append(i)
            if i == last_page or last_page == 0:
                break

    return render_template('snapshots_show.html',
                           page=page, page_size=page_size, keyword=keyword, pages=pages, order_by=order_by, order=order,
                           last_page=last_page, snapshots_ret=snapshots_ret,
                           guests_mapping_by_uuid=guests_mapping_by_uuid)


