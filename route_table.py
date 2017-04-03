#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule
from views import config
from views import guest
from views import os_init
from views import os_init_write
from views import os_template


__author__ = 'James Iter'
__date__ = '2017/03/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


# JimV 配置操作
add_rule(config.blueprint, '', view_func='config.r_create', methods=['POST'])
# 只有一条记录，所以不指定 id
add_rule(config.blueprint, '', view_func='config.r_update', methods=['PATCH'])
add_rule(config.blueprint, '', view_func='config.r_get', methods=['GET'])

# 系统初始化配置操作
add_rule(os_init.blueprint, '', view_func='os_init.r_create', methods=['POST'])
add_rule(os_init.blueprint, '/<_id>', view_func='os_init.r_update', methods=['PATCH'])
add_rule(os_init.blueprint, '/<_id>', view_func='os_init.r_delete', methods=['DELETE'])
add_rule(os_init.blueprint, '', view_func='os_init.r_get_by_filter', methods=['GET'])

add_rule(os_init_write.blueprint, '', view_func='os_init_write.r_create', methods=['POST'])
add_rule(os_init_write.blueprint, '/<_id>', view_func='os_init_write.r_update', methods=['PATCH'])
add_rule(os_init_write.blueprint, '/<_id>', view_func='os_init_write.r_delete', methods=['DELETE'])
add_rule(os_init_write.blueprint, '', view_func='os_init_write.r_get_by_filter', methods=['GET'])

# 系统模板操作
add_rule(os_template.blueprint, '', view_func='os_template.r_create', methods=['POST'])
add_rule(os_template.blueprint, '/<_id>', view_func='os_template.r_update', methods=['PATCH'])
add_rule(os_template.blueprint, '/<_id>', view_func='os_template.r_delete', methods=['DELETE'])
add_rule(os_template.blueprint, '', view_func='os_template.r_get_by_filter', methods=['GET'])

# Guest操作
# 创建虚拟机
add_rule(guest.blueprint, '', view_func='guest.r_create', methods=['POST'])

