#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule_api
from api import config
from api import guest
from api import disk
from api import os_init
from api import os_init_write
from api import os_template
from api import log


__author__ = 'James Iter'
__date__ = '2017/03/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


# JimV 配置操作
add_rule_api(config.blueprint, '', api_func='config.r_create', methods=['POST'])
# 只有一条记录，所以不指定 id
add_rule_api(config.blueprint, '', api_func='config.r_update', methods=['PATCH'])
add_rule_api(config.blueprint, '', api_func='config.r_get', methods=['GET'])

# 系统初始化配置操作
add_rule_api(os_init.blueprint, '', api_func='os_init.r_create', methods=['POST'])
add_rule_api(os_init.blueprint, '/<_id>', api_func='os_init.r_update', methods=['PATCH'])
add_rule_api(os_init.blueprint, '/<_id>', api_func='os_init.r_delete', methods=['DELETE'])
add_rule_api(os_init.blueprints, '/<ids>', api_func='os_init.r_get', methods=['GET'])
add_rule_api(os_init.blueprints, '', api_func='os_init.r_get_by_filter', methods=['GET'])
add_rule_api(os_init.blueprints, '/_search', api_func='os_init.r_content_search', methods=['GET'])

add_rule_api(os_init_write.blueprint, '', api_func='os_init_write.r_create', methods=['POST'])
add_rule_api(os_init_write.blueprint, '/<_id>', api_func='os_init_write.r_update', methods=['PATCH'])
add_rule_api(os_init_write.blueprint, '/<_id>', api_func='os_init_write.r_delete', methods=['DELETE'])
add_rule_api(os_init_write.blueprints, '/<ids>', api_func='os_init_write.r_get', methods=['GET'])
add_rule_api(os_init_write.blueprints, '', api_func='os_init_write.r_get_by_filter', methods=['GET'])
add_rule_api(os_init_write.blueprints, '/_search', api_func='os_init_write.r_content_search', methods=['GET'])

# 系统模板操作
add_rule_api(os_template.blueprint, '', api_func='os_template.r_create', methods=['POST'])
add_rule_api(os_template.blueprint, '/<_id>', api_func='os_template.r_update', methods=['PATCH'])
add_rule_api(os_template.blueprint, '/<_id>', api_func='os_template.r_delete', methods=['DELETE'])
add_rule_api(os_template.blueprints, '/<ids>', api_func='os_template.r_get', methods=['GET'])
add_rule_api(os_template.blueprints, '', api_func='os_template.r_get_by_filter', methods=['GET'])
add_rule_api(os_template.blueprints, '/_search', api_func='os_template.r_content_search', methods=['GET'])

# Guest操作
# 创建虚拟机
add_rule_api(guest.blueprint, '', api_func='guest.r_create', methods=['POST'])
add_rule_api(guest.blueprints, '/_reboot/<uuids>', api_func='guest.r_reboot', methods=['PUT'])
add_rule_api(guest.blueprints, '/_force_reboot/<uuids>', api_func='guest.r_force_reboot', methods=['PUT'])
add_rule_api(guest.blueprints, '/_shutdown/<uuids>', api_func='guest.r_shutdown', methods=['PUT'])
add_rule_api(guest.blueprints, '/_force_shutdown/<uuids>', api_func='guest.r_force_shutdown', methods=['PUT'])
add_rule_api(guest.blueprints, '/_boot/<uuids>', api_func='guest.r_boot', methods=['PUT'])
add_rule_api(guest.blueprints, '/_suspend/<uuids>', api_func='guest.r_suspend', methods=['PUT'])
add_rule_api(guest.blueprints, '/_resume/<uuids>', api_func='guest.r_resume', methods=['PUT'])
add_rule_api(guest.blueprint, '/_attach_disk/<uuid>/<disk_uuid>', api_func='guest.r_attach_disk', methods=['PUT'])
add_rule_api(guest.blueprint, '/_detach_disk/<disk_uuid>', api_func='guest.r_detach_disk', methods=['PUT'])
add_rule_api(guest.blueprints, '/_migrate/<uuids>/<destination_host>', api_func='guest.r_migrate', methods=['PUT'])
add_rule_api(guest.blueprints, '/<uuids>', api_func='guest.r_get', methods=['GET'])
add_rule_api(guest.blueprints, '', api_func='guest.r_get_by_filter', methods=['GET'])
add_rule_api(guest.blueprints, '/_search', api_func='guest.r_content_search', methods=['GET'])
add_rule_api(guest.blueprint, '/<uuid>', api_func='guest.r_update', methods=['PATCH'])
add_rule_api(guest.blueprints, '/<uuids>', api_func='guest.r_delete', methods=['DELETE'])

# Disk操作
add_rule_api(disk.blueprint, '', api_func='disk.r_create', methods=['POST'])
add_rule_api(disk.blueprint, '/_disk_resize/<uuid>/<size>', api_func='disk.r_resize', methods=['PUT'])
add_rule_api(disk.blueprints, '/<uuids>', api_func='disk.r_delete', methods=['DELETE'])
add_rule_api(disk.blueprint, '/<uuid>', api_func='disk.r_update', methods=['PATCH'])
add_rule_api(disk.blueprints, '/<uuids>', api_func='disk.r_get', methods=['GET'])
add_rule_api(disk.blueprints, '', api_func='disk.r_get_by_filter', methods=['GET'])
add_rule_api(disk.blueprints, '/_search', api_func='disk.r_content_search', methods=['GET'])

# 日志查询
# 系统模板操作
add_rule_api(log.blueprints, '/<ids>', api_func='log.r_get', methods=['GET'])
add_rule_api(log.blueprints, '', api_func='log.r_get_by_filter', methods=['GET'])
add_rule_api(log.blueprints, '/_search', api_func='log.r_content_search', methods=['GET'])

