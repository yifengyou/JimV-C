#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule_views
from views import guest, disk, log, os_template, boot_job, operate_rule


__author__ = 'James Iter'
__date__ = '2017/03/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


add_rule_views(guest.blueprints, '', views_func='guest.show', methods=['GET'])
add_rule_views(guest.blueprints, '/create', views_func='guest.create', methods=['GET', 'POST'])
add_rule_views(guest.blueprints, '/success', views_func='guest.success', methods=['GET'])
add_rule_views(guest.blueprint, '/vnc/<uuid>', views_func='guest.vnc', methods=['GET'])
add_rule_views(guest.blueprint, '/detail/<uuid>', views_func='guest.detail', methods=['GET'])
add_rule_views(guest.blueprint, '/boot_jobs/<uuid>', views_func='guest.show_boot_job', methods=['GET'])

add_rule_views(disk.blueprints, '', views_func='disk.show', methods=['GET'])
add_rule_views(disk.blueprints, '/create', views_func='disk.create', methods=['GET', 'POST'])
add_rule_views(disk.blueprint, '/detail/<uuid>', views_func='disk.detail', methods=['GET', 'POST'])

add_rule_views(log.blueprints, '', views_func='log.show', methods=['GET'])

add_rule_views(os_template.blueprints, '', views_func='os_template.show', methods=['GET'])
add_rule_views(os_template.blueprint, '', views_func='os_template.create', methods=['POST'])

add_rule_views(boot_job.blueprints, '', views_func='boot_job.show', methods=['GET'])
add_rule_views(boot_job.blueprint, '', views_func='boot_job.create', methods=['POST'])

add_rule_views(operate_rule.blueprints, '', views_func='operate_rule.show', methods=['GET'])
add_rule_views(operate_rule.blueprint, '', views_func='operate_rule.create', methods=['POST'])

