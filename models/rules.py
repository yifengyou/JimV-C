#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import Enum


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Rules(Enum):
    OFFSET = ('regex:^\d{1,17}$', 'offset')
    LIMIT = ('regex:^\d{1,17}$', 'limit')
    PAGE = ('regex:^\d{1,17}$', 'page')
    PAGE_SIZE = ('regex:^\d{1,17}$', 'page_size')
    ORDER_BY = (basestring, 'order_by', (1, 30))
    ORDER = (basestring, 'order', ['asc', 'desc'])
    KEYWORD = (basestring, 'keyword')

    ID = ('regex:^\d{1,17}$', 'id')

    # 正则表达式方便校验其来自URL的参数
    IP = 'regex:^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$'

    CONFIG_ID = (int, 'id')
    GLUSTERFS_VOLUME = (basestring, 'glusterfs_volume')
    VM_NETWORK = (basestring, 'vm_network')
    VM_MANAGE_NETWORK = (basestring, 'vm_manage_network')
    START_IP = (IP, 'start_ip')
    END_IP = (IP, 'end_ip')
    START_VNC_PORT = (int, 'start_vnc_port')
    NETMASK = (IP, 'netmask')
    GATEWAY = (IP, 'gateway')
    DNS1 = (IP, 'dns1')
    DNS2 = (IP, 'dns2')
    RSA_PRIVATE = (basestring, 'rsa_private')
    RSA_PUBLIC = (basestring, 'rsa_public')

    UUID = (basestring, 'uuid', (36, 36))
    UUIDS = ('regex:^([\w-]{36})(,[\w-]{36})*$', 'uuids')
    CPU = (int, 'cpu')
    MEMORY = (int, 'memory')
    OS_TEMPLATE_ID = (int, 'os_template_id')
    QUANTITY = (int, 'quantity')
    NAME = (basestring, 'name')
    PASSWORD = (basestring, 'password')
    LEASE_TERM = (int, 'lease_term')
    DESTINATION_HOST = (basestring, 'destination_host', (5, 64))
    DISK_UUID = (basestring, 'disk_uuid', (36, 36))
    DISK_SIZE = (int, 'size')
    DISK_SIZE_STR = ('regex:^\d{1,17}$', 'size')

    REMARK = (basestring, 'remark')
    LABEL = (basestring, 'label')
    ACTIVE = (bool, 'active')

    OS_INIT_ID_EXT = (int, 'os_init_id')
    OS_INIT_WRITE_PATH = (basestring, 'path')
    OS_INIT_WRITE_CONTENT = (basestring, 'content')

