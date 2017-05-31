#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule_views
from views import guest


__author__ = 'James Iter'
__date__ = '2017/03/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


add_rule_views(guest.blueprints, '', views_func='guest.show', methods=['GET'])

