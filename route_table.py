#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule
from views import config
from views import guest
from views import os_init
from views import os_init_write
from views import os_template
from views import log


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
add_rule(os_init.blueprints, '', view_func='os_init.r_get_by_filter', methods=['GET'])

add_rule(os_init_write.blueprint, '', view_func='os_init_write.r_create', methods=['POST'])
add_rule(os_init_write.blueprint, '/<_id>', view_func='os_init_write.r_update', methods=['PATCH'])
add_rule(os_init_write.blueprint, '/<_id>', view_func='os_init_write.r_delete', methods=['DELETE'])
add_rule(os_init_write.blueprints, '', view_func='os_init_write.r_get_by_filter', methods=['GET'])

# 系统模板操作
add_rule(os_template.blueprint, '', view_func='os_template.r_create', methods=['POST'])
add_rule(os_template.blueprint, '/<_id>', view_func='os_template.r_update', methods=['PATCH'])
add_rule(os_template.blueprint, '/<_id>', view_func='os_template.r_delete', methods=['DELETE'])
add_rule(os_template.blueprints, '', view_func='os_template.r_get_by_filter', methods=['GET'])

# Guest操作
# 创建虚拟机
add_rule(guest.blueprint, '', view_func='guest.r_create', methods=['POST'])
add_rule(guest.blueprint, '/_reboot/<uuid>', view_func='guest.r_reboot', methods=['PUT'])
add_rule(guest.blueprint, '/_force_reboot/<uuid>', view_func='guest.r_force_reboot', methods=['PUT'])
add_rule(guest.blueprint, '/_shutdown/<uuid>', view_func='guest.r_shutdown', methods=['PUT'])
add_rule(guest.blueprint, '/_force_shutdown/<uuid>', view_func='guest.r_force_shutdown', methods=['PUT'])
add_rule(guest.blueprint, '/_boot/<uuid>', view_func='guest.r_boot', methods=['PUT'])
add_rule(guest.blueprint, '/_suspend/<uuid>', view_func='guest.r_suspend', methods=['PUT'])
add_rule(guest.blueprint, '/_resume/<uuid>', view_func='guest.r_resume', methods=['PUT'])
add_rule(guest.blueprint, '/_delete/<uuid>', view_func='guest.r_delete', methods=['PUT'])
add_rule(guest.blueprint, '/_disk_resize/<uuid>', view_func='guest.r_disk_resize', methods=['PUT'])
add_rule(guest.blueprint, '/_attach_disk/<uuid>', view_func='guest.r_attach_disk', methods=['PUT'])
add_rule(guest.blueprint, '/_detach_disk/<uuid>', view_func='guest.r_detach_disk', methods=['PUT'])
add_rule(guest.blueprint, '/_migrate/<uuid>', view_func='guest.r_migrate', methods=['PUT'])

# 日志查询
# 系统模板操作
add_rule(log.blueprints, '', view_func='log.r_get_by_filter', methods=['GET'])
add_rule(log.blueprints, '/_search', view_func='log.r_content_search', methods=['GET'])

