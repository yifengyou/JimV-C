#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule_api
from api import config
from api import user
from api import guest
from api import disk
from api import os_template_image
from api import os_template_profile
from api import os_template_initialize_operate_set
from api import os_template_initialize_operate
from api import log
from api import host
from api import guest_performance
from api import host_performance
from api import ssh_key


__author__ = 'James Iter'
__date__ = '2017/03/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


# JimV 配置操作
add_rule_api(config.blueprint, '', api_func='config.r_create', methods=['POST'])
# 只有一条记录，所以不指定 id
add_rule_api(config.blueprint, '', api_func='config.r_update', methods=['PATCH'])
add_rule_api(config.blueprint, '/_quota', api_func='config.r_update_quota', methods=['PATCH'])
add_rule_api(config.blueprint, '', api_func='config.r_get', methods=['GET'])

# 用户管理
add_rule_api(user.blueprint, '/_sign_in', api_func='user.r_sign_in', methods=['POST'])
add_rule_api(user.blueprint, '/_sign_out', api_func='user.r_sign_out', methods=['GET'])
add_rule_api(user.blueprint, '/_change_password', api_func='user.r_change_password', methods=['POST'])
add_rule_api(user.blueprint, '/_reset_password/<token>', api_func='user.r_reset_password', methods=['POST'])
add_rule_api(user.blueprint, '/_send_reset_password_email/<login_name>', api_func='user.r_send_reset_password_email',
             methods=['PUT'])

# 系统模板镜像操作
add_rule_api(os_template_image.blueprint, '', api_func='os_template_image.r_create', methods=['POST'])
add_rule_api(os_template_image.blueprint, '/<_id>', api_func='os_template_image.r_update', methods=['PATCH'])
add_rule_api(os_template_image.blueprints, '/<ids>', api_func='os_template_image.r_delete', methods=['DELETE'])
add_rule_api(os_template_image.blueprints, '/<ids>', api_func='os_template_image.r_get', methods=['GET'])
add_rule_api(os_template_image.blueprints, '', api_func='os_template_image.r_get_by_filter', methods=['GET'])
add_rule_api(os_template_image.blueprints, '/_search', api_func='os_template_image.r_content_search', methods=['GET'])

# 系统模板描述文件操作
add_rule_api(os_template_profile.blueprint, '', api_func='os_template_profile.r_create', methods=['POST'])
add_rule_api(os_template_profile.blueprint, '/<_id>', api_func='os_template_profile.r_update', methods=['PATCH'])
add_rule_api(os_template_profile.blueprints, '/<ids>', api_func='os_template_profile.r_delete', methods=['DELETE'])
add_rule_api(os_template_profile.blueprints, '/<ids>', api_func='os_template_profile.r_get', methods=['GET'])
add_rule_api(os_template_profile.blueprints, '', api_func='os_template_profile.r_get_by_filter', methods=['GET'])
add_rule_api(os_template_profile.blueprints, '/_search', api_func='os_template_profile.r_content_search',
             methods=['GET'])

# 系统模板初始化操作集操作
add_rule_api(os_template_initialize_operate_set.blueprint, '',
             api_func='os_template_initialize_operate_set.r_create', methods=['POST'])
add_rule_api(os_template_initialize_operate_set.blueprint, '/<_id>',
             api_func='os_template_initialize_operate_set.r_update', methods=['PATCH'])
add_rule_api(os_template_initialize_operate_set.blueprints, '/<ids>',
             api_func='os_template_initialize_operate_set.r_delete', methods=['DELETE'])
add_rule_api(os_template_initialize_operate_set.blueprints, '/<ids>',
             api_func='os_template_initialize_operate_set.r_get', methods=['GET'])
add_rule_api(os_template_initialize_operate_set.blueprints, '',
             api_func='os_template_initialize_operate_set.r_get_by_filter', methods=['GET'])
add_rule_api(os_template_initialize_operate_set.blueprints, '/_search',
             api_func='os_template_initialize_operate_set.r_content_search', methods=['GET'])

# 系统模板初始化操作细则
add_rule_api(os_template_initialize_operate.blueprint, '',
             api_func='os_template_initialize_operate.r_create', methods=['POST'])
add_rule_api(os_template_initialize_operate.blueprint, '/<_id>',
             api_func='os_template_initialize_operate.r_update', methods=['PATCH'])
add_rule_api(os_template_initialize_operate.blueprints, '/<ids>',
             api_func='os_template_initialize_operate.r_delete', methods=['DELETE'])
add_rule_api(os_template_initialize_operate.blueprints, '/<ids>',
             api_func='os_template_initialize_operate.r_get', methods=['GET'])
add_rule_api(os_template_initialize_operate.blueprints, '',
             api_func='os_template_initialize_operate.r_get_by_filter', methods=['GET'])
add_rule_api(os_template_initialize_operate.blueprints, '/_search',
             api_func='os_template_initialize_operate.r_content_search', methods=['GET'])

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
add_rule_api(guest.blueprints, '/_boot_jobs/<uuids>/<boot_jobs_id>', api_func='guest.r_add_boot_jobs', methods=['PUT'])
add_rule_api(guest.blueprints, '/_boot_jobs/<uuids>', api_func='guest.r_get_boot_jobs', methods=['GET'])
add_rule_api(guest.blueprints, '/_boot_jobs/<uuids>/<boot_jobs_id>', api_func='guest.r_delete_boot_jobs',
             methods=['DELETE'])
add_rule_api(guest.blueprints, '/_boot_jobs/uuids', api_func='guest.r_get_uuids_of_all_had_boot_job', methods=['GET'])
add_rule_api(guest.blueprints, '/_reset_password/<uuids>/<password>', api_func='guest.r_reset_password',
             methods=['PUT'])
add_rule_api(guest.blueprints, '/_distribute_count', api_func='guest.r_distribute_count', methods=['GET'])

# Disk操作
add_rule_api(disk.blueprint, '', api_func='disk.r_create', methods=['POST'])
add_rule_api(disk.blueprint, '/_disk_resize/<uuid>/<size>', api_func='disk.r_resize', methods=['PUT'])
add_rule_api(disk.blueprints, '/<uuids>', api_func='disk.r_delete', methods=['DELETE'])
add_rule_api(disk.blueprints, '/<uuids>', api_func='disk.r_update', methods=['PATCH'])
add_rule_api(disk.blueprints, '/<uuids>', api_func='disk.r_get', methods=['GET'])
add_rule_api(disk.blueprints, '', api_func='disk.r_get_by_filter', methods=['GET'])
add_rule_api(disk.blueprints, '/_search', api_func='disk.r_content_search', methods=['GET'])
add_rule_api(disk.blueprints, '/_distribute_count', api_func='disk.r_distribute_count', methods=['GET'])

# 日志查询
# 系统模板操作
add_rule_api(log.blueprints, '/<ids>', api_func='log.r_get', methods=['GET'])
add_rule_api(log.blueprints, '', api_func='log.r_get_by_filter', methods=['GET'])
add_rule_api(log.blueprints, '/_search', api_func='log.r_content_search', methods=['GET'])

# 计算节点操作
add_rule_api(host.blueprints, '/<nodes_id>', api_func='host.r_get', methods=['GET'])
add_rule_api(host.blueprints, '', api_func='host.r_get_by_filter', methods=['GET'])
add_rule_api(host.blueprints, '/_search', api_func='host.r_content_search', methods=['GET'])
add_rule_api(host.blueprints, '/<nodes_id>', api_func='host.r_delete', methods=['DELETE'])
add_rule_api(host.blueprints, '/<hosts_name>/<random>', api_func='host.r_nonrandom', methods=['PUT'])

# SSH Key 操作
add_rule_api(ssh_key.blueprint, '', api_func='ssh_key.r_create', methods=['POST'])
add_rule_api(ssh_key.blueprints, '/<ids>', api_func='ssh_key.r_delete', methods=['DELETE'])
add_rule_api(ssh_key.blueprints, '/<_id>', api_func='ssh_key.r_update', methods=['PATCH'])
add_rule_api(ssh_key.blueprints, '/<ids>', api_func='ssh_key.r_get', methods=['GET'])
add_rule_api(ssh_key.blueprints, '', api_func='ssh_key.r_get_by_filter', methods=['GET'])
add_rule_api(ssh_key.blueprints, '/_search', api_func='ssh_key.r_content_search', methods=['GET'])

# 日志查询
# Guest 性能查询
add_rule_api(guest_performance.blueprint, '/cpu_memory',
             api_func='guest_performance.r_cpu_memory_get_by_filter', methods=['GET'])
add_rule_api(guest_performance.blueprint, '/traffic',
             api_func='guest_performance.r_traffic_get_by_filter', methods=['GET'])
add_rule_api(guest_performance.blueprint, '/disk_io',
             api_func='guest_performance.r_disk_io_get_by_filter', methods=['GET'])
add_rule_api(guest_performance.blueprint, '/cpu_memory/last_hour/<uuid>',
             api_func='guest_performance.r_cpu_memory_last_hour', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/cpu_memory/last_six_hours/<uuid>',
             api_func='guest_performance.r_cpu_memory_last_six_hours', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/cpu_memory/last_day/<uuid>',
             api_func='guest_performance.r_cpu_memory_last_day', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/cpu_memory/last_seven_days/<uuid>',
             api_func='guest_performance.r_cpu_memory_last_seven_days', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/traffic/last_hour/<uuid>',
             api_func='guest_performance.r_traffic_last_hour', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/traffic/last_six_hours/<uuid>',
             api_func='guest_performance.r_traffic_last_six_hours', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/traffic/last_day/<uuid>',
             api_func='guest_performance.r_traffic_last_day', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/traffic/last_seven_days/<uuid>',
             api_func='guest_performance.r_traffic_last_seven_days', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/disk_io/last_hour/<uuid>',
             api_func='guest_performance.r_disk_io_last_hour', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/disk_io/last_six_hours/<uuid>',
             api_func='guest_performance.r_disk_io_last_six_hours', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/disk_io/last_day/<uuid>',
             api_func='guest_performance.r_disk_io_last_day', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/disk_io/last_seven_days/<uuid>',
             api_func='guest_performance.r_disk_io_last_seven_days', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/_current_top_10',
             api_func='guest_performance.r_current_top_10', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/_last_10_minutes_top_10',
             api_func='guest_performance.r_last_10_minutes_top_10', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/_last_hour_top_10',
             api_func='guest_performance.r_last_hour_top_10', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/_last_six_hours_top_10',
             api_func='guest_performance.r_last_six_hours_top_10', methods=['GET'])

add_rule_api(guest_performance.blueprint, '/_last_day_top_10',
             api_func='guest_performance.r_last_day_top_10', methods=['GET'])

# Host 性能查询
add_rule_api(host_performance.blueprint, '/cpu_memory', api_func='host_performance.r_cpu_memory_get_by_filter',
             methods=['GET'])
add_rule_api(host_performance.blueprint, '/traffic', api_func='host_performance.r_traffic_get_by_filter',
             methods=['GET'])
add_rule_api(host_performance.blueprint, '/disk_io', api_func='host_performance.r_disk_usage_io_get_by_filter',
             methods=['GET'])
add_rule_api(host_performance.blueprint, '/cpu_memory/last_hour/<node_id>',
             api_func='host_performance.r_cpu_memory_last_hour', methods=['GET'])

add_rule_api(host_performance.blueprint, '/cpu_memory/last_six_hours/<node_id>',
             api_func='host_performance.r_cpu_memory_last_six_hours', methods=['GET'])

add_rule_api(host_performance.blueprint, '/cpu_memory/last_day/<node_id>',
             api_func='host_performance.r_cpu_memory_last_day', methods=['GET'])

add_rule_api(host_performance.blueprint, '/cpu_memory/last_seven_days/<node_id>',
             api_func='host_performance.r_cpu_memory_last_seven_days', methods=['GET'])

add_rule_api(host_performance.blueprint, '/traffic/last_hour/<node_id>/<nic_name>',
             api_func='host_performance.r_traffic_last_hour', methods=['GET'])

add_rule_api(host_performance.blueprint, '/traffic/last_six_hours/<node_id>/<nic_name>',
             api_func='host_performance.r_traffic_last_six_hours', methods=['GET'])

add_rule_api(host_performance.blueprint, '/traffic/last_day/<node_id>/<nic_name>',
             api_func='host_performance.r_traffic_last_day', methods=['GET'])

add_rule_api(host_performance.blueprint, '/traffic/last_seven_days/<node_id>/<nic_name>',
             api_func='host_performance.r_traffic_last_seven_days', methods=['GET'])

add_rule_api(host_performance.blueprint, '/disk_io/last_hour/<node_id>/<path:mountpoint>',
             api_func='host_performance.r_disk_usage_io_last_hour', methods=['GET'])

add_rule_api(host_performance.blueprint, '/disk_io/last_six_hours/<node_id>/<mountpoint>',
             api_func='host_performance.r_disk_usage_io_last_six_hours', methods=['GET'])

add_rule_api(host_performance.blueprint, '/disk_io/last_day/<node_id>/<mountpoint>',
             api_func='host_performance.r_disk_usage_io_last_day', methods=['GET'])

add_rule_api(host_performance.blueprint, '/disk_io/last_seven_days/<node_id>/<mountpoint>',
             api_func='host_performance.r_disk_usage_io_last_seven_days', methods=['GET'])

add_rule_api(host_performance.blueprint, '/_current_top_10',
             api_func='host_performance.r_current_top_10', methods=['GET'])

add_rule_api(host_performance.blueprint, '/_last_10_minutes_top_10',
             api_func='host_performance.r_last_10_minutes_top_10', methods=['GET'])

add_rule_api(host_performance.blueprint, '/_last_hour_top_10',
             api_func='host_performance.r_last_hour_top_10', methods=['GET'])

add_rule_api(host_performance.blueprint, '/_last_six_hours_top_10',
             api_func='host_performance.r_last_six_hours_top_10', methods=['GET'])

add_rule_api(host_performance.blueprint, '/_last_day_top_10',
             api_func='host_performance.r_last_day_top_10', methods=['GET'])


