#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import Enum


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Rules(Enum):
    # 正则表达式方便校验其来自URL的参数
    REG_NUMBER = 'regex:^\d{1,17}$'
    REG_NUMBERS = 'regex:^(\d{1,17})(,\d{1,17})*$'
    REG_UUIDS = 'regex:^([\w-]{36})(,[\w-]{36})*$'
    REG_IP = 'regex:^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$'

    OFFSET = (REG_NUMBER, 'offset')
    LIMIT = (REG_NUMBER, 'limit')
    PAGE = (REG_NUMBER, 'page')
    PAGE_SIZE = (REG_NUMBER, 'page_size')
    ORDER_BY = (basestring, 'order_by', (1, 30))
    ORDER = (basestring, 'order', ['asc', 'desc'])
    KEYWORD = (basestring, 'keyword')

    ID = (REG_NUMBER, 'id')
    IDS = (REG_NUMBERS, 'ids')
    BOOT_JOBS_ID = (REG_NUMBERS, 'boot_jobs_id')

    CONFIG_ID = (int, 'id')
    JIMV_EDITION = (int, 'jimv_edition')
    STORAGE_MODE = (int, 'storage_mode')
    DFS_VOLUME = (basestring, 'dfs_volume')
    STORAGE_PATH = (basestring, 'storage_path')
    VM_NETWORK = (basestring, 'vm_network')
    VM_MANAGE_NETWORK = (basestring, 'vm_manage_network')
    START_IP = (REG_IP, 'start_ip')
    END_IP = (REG_IP, 'end_ip')
    START_VNC_PORT = (int, 'start_vnc_port')
    NETMASK = (REG_IP, 'netmask')
    GATEWAY = (REG_IP, 'gateway')
    DNS1 = (REG_IP, 'dns1')
    DNS2 = (REG_IP, 'dns2')
    IOPS_BASE = (int, 'iops_base')
    IOPS_PRE_UNIT = (int, 'iops_pre_unit')
    IOPS_CAP = (int, 'iops_cap')
    IOPS_MAX = (int, 'iops_max')
    IOPS_MAX_LENGTH = (int, 'iops_max_length')
    BPS_BASE = (int, 'iops_base')
    BPS_PRE_UNIT = (int, 'iops_pre_unit')
    BPS_CAP = (int, 'iops_cap')
    BPS_MAX = (int, 'iops_max')
    BPS_MAX_LENGTH = (int, 'iops_max_length')
    RSA_PRIVATE = (basestring, 'rsa_private')
    RSA_PUBLIC = (basestring, 'rsa_public')

    UUID = (basestring, 'uuid', (36, 36))
    NODE_ID = (basestring, 'node_id', (14, 15))
    UUIDS = (REG_UUIDS, 'uuids')
    CPU = (int, 'cpu')
    MEMORY = (int, 'memory')
    OS_TEMPLATE_ID = (int, 'os_template_id')
    QUANTITY = (int, 'quantity')
    NAME = (basestring, 'name')
    PATH = (basestring, 'path')
    LOGIN_NAME = (basestring, 'login_name')
    PASSWORD = (basestring, 'password')
    LEASE_TERM = (int, 'lease_term')
    GUEST_ON_HOST = (basestring, 'on_host', (1, 128))
    DESTINATION_HOST = (basestring, 'destination_host', (5, 64))
    DISK_UUID = (basestring, 'disk_uuid', (36, 36))
    DISK_SIZE = (int, 'size')
    DISK_SIZE_STR = (REG_NUMBER, 'size')
    DISK_ON_HOST = (basestring, 'on_host', (1, 128))
    IOPS = (int, 'iops')
    IOPS_RD = (int, 'iops_rd')
    IOPS_WR = (int, 'iops_wr')
    BPS = (int, 'bps')
    BPS_RD = (int, 'bps_rd')
    BPS_WR = (int, 'bps_wr')
    INFLUENCE_CURRENT_GUEST = (bool, 'influence_current_guest')

    REMARK = (basestring, 'remark')
    USE_FOR = (int, 'use_for')
    LABEL = (basestring, 'label')
    OS_TYPE = (int, 'os_type')
    ACTIVE = (bool, 'active')
    ICON = (basestring, 'icon')

    BOOT_JOB_ID_EXT = (int, 'boot_job_id')
    OPERATE_RULE_KIND = (int, 'kind')
    OPERATE_RULE_SEQUENCE = (int, 'sequence')
    OPERATE_RULE_PATH = (basestring, 'path')
    OPERATE_RULE_CONTENT = (basestring, 'content')
    OPERATE_RULE_COMMAND = (basestring, 'command')

    TOKEN = (basestring, 'token')

