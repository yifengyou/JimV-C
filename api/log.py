#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint

from api.base import Base
from models import Log
from models import Rules
from models import Utils


__author__ = 'James Iter'
__date__ = '2017/4/8'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'log',
    __name__,
    url_prefix='/api/log'
)

blueprints = Blueprint(
    'logs',
    __name__,
    url_prefix='/api/logs'
)


log_base = Base(the_class=Log, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_get(ids):
    return log_base.get(ids=ids, ids_rule=Rules.IDS.value, by_field='id')


@Utils.dumps2response
def r_get_by_filter():
    return log_base.get_by_filter()


@Utils.dumps2response
def r_content_search():
    return log_base.content_search()

