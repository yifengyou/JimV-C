#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule_views
from views import guest
from views import disk
from views import log
from views import host
from views import dashboard
from views import config
from views import misc
from views import os_template_image
from views import ssh_key
from views import snapshot


__author__ = 'James Iter'
__date__ = '2017/03/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


add_rule_views(config.blueprint, '', views_func='config.show', methods=['GET'])
add_rule_views(config.blueprint, '/create', views_func='config.create', methods=['GET', 'POST'])

add_rule_views(misc.blueprint, 'login', views_func='misc.login', methods=['GET'])
add_rule_views(misc.blueprint, 'change_password', views_func='misc.change_password', methods=['GET'])
add_rule_views(misc.blueprint, 'recover_password', views_func='misc.recover_password', methods=['GET', 'POST'])
add_rule_views(misc.blueprint, 'reset_password/<token>', views_func='misc.reset_password', methods=['GET', 'POST'])

add_rule_views(dashboard.blueprint, '', views_func='dashboard.show', methods=['GET'])

add_rule_views(guest.blueprints, '', views_func='guest.show', methods=['GET'])
add_rule_views(guest.blueprints, '/create', views_func='guest.create', methods=['GET', 'POST'])
add_rule_views(guest.blueprints, '/success', views_func='guest.success', methods=['GET'])
add_rule_views(guest.blueprint, '/vnc/<uuid>', views_func='guest.vnc', methods=['GET'])
add_rule_views(guest.blueprint, '/detail/<uuid>', views_func='guest.detail', methods=['GET'])

add_rule_views(disk.blueprints, '', views_func='disk.show', methods=['GET'])
add_rule_views(disk.blueprints, '/create', views_func='disk.create', methods=['GET', 'POST'])
add_rule_views(disk.blueprint, '/detail/<uuid>', views_func='disk.detail', methods=['GET', 'POST'])

add_rule_views(log.blueprints, '', views_func='log.show', methods=['GET'])

add_rule_views(os_template_image.blueprints, '', views_func='os_template_image.show', methods=['GET'])
add_rule_views(os_template_image.blueprint, '', views_func='os_template_image.create', methods=['POST'])

add_rule_views(host.blueprints, '', views_func='host.show', methods=['GET'])
add_rule_views(host.blueprint, '/detail/<node_id>', views_func='host.detail', methods=['GET'])

add_rule_views(ssh_key.blueprints, '', views_func='ssh_key.show', methods=['GET'])
add_rule_views(ssh_key.blueprint, '', views_func='ssh_key.create', methods=['POST'])

add_rule_views(snapshot.blueprints, '', views_func='snapshot.show', methods=['GET'])
