#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji
from flask import Blueprint

from jimvc.models import Utils


__author__ = 'James Iter'
__date__ = '2018/10/2'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


blueprint = Blueprint(
    'api_about',
    __name__,
    url_prefix='/api/about'
)

blueprints = Blueprint(
    'api_abouts',
    __name__,
    url_prefix='/api/abouts'
)


@Utils.dumps2response
def r_get():
    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = {
        'version': 0.7,
        'desc': """
    JimV 是一套舒适的驾驭系统。通过它，您可以轻松自如地，让那匹彪悍烈马，把您带上长空云霄。
    "舒适"，是设计 JimV 的哲学理念。其中包含的意义有 "平滑、自在、敏捷、可控"。您所想、所要的，
只需轻触鼠标，即可信手捏来。""",
        'copyright': '版权所有2018 JamesIter. 保留所有权利。'
    }

    return ret
