#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import Enum


__author__ = 'James Iter'
__date__ = '2017/3/21'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


# TODO: 考虑按视角归类，比如自身视角名称(uuid)，外部视角名称(guest_uuid)
class Rules(Enum):
    # 正则表达式方便校验其来自URL的参数
    REG_NUMBER = 'regex:^\d{1,17}$'
    REG_NUMBERS = 'regex:^(\d{1,17})(,\d{1,17})*$'
    REG_UUIDS = 'regex:^([\w-]{36})(,[\w-]{36})*$'
    REG_HOSTS_NAME = 'regex:^([\S-]{1,128})(,[\S-]{1,128})*$'
    REG_IP = 'regex:^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$'

    OFFSET = (REG_NUMBER, 'offset')
    LIMIT = (REG_NUMBER, 'limit')
    PAGE = (REG_NUMBER, 'page')
    PAGE_SIZE = (REG_NUMBER, 'page_size')
    ORDER_BY = (str, 'order_by', (1, 30))
    ORDER = (str, 'order', ['asc', 'desc'])
    KEYWORD = (str, 'keyword')

    ID = (REG_NUMBER, 'id')
    IDS = (REG_NUMBERS, 'ids')
    TTL = (REG_NUMBER, 'ttl')
    HOSTS_NAME = (REG_HOSTS_NAME, 'hosts_name')

    CONFIG_ID = (int, 'id')
    JIMV_EDITION = (int, 'jimv_edition')
    STORAGE_MODE = (int, 'storage_mode')
    DFS_VOLUME = (str, 'dfs_volume')
    STORAGE_PATH = (str, 'storage_path')
    VM_NETWORK = (str, 'vm_network')
    VM_MANAGE_NETWORK = (str, 'vm_manage_network')
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
    BANDWIDTH = (int, 'bandwidth')
    BANDWIDTH_IN_URL = (REG_NUMBER, 'bandwidth')
    BANDWIDTH_UNIT = (str, 'bandwidth_unit', ['k', 'm', 'g'])

    IP = (REG_IP, 'ip')
    START_IP = (REG_IP, 'start_ip')
    END_IP = (REG_IP, 'end_ip')
    START_VNC_PORT = (int, 'start_vnc_port')
    NETMASK = (REG_IP, 'netmask')
    GATEWAY = (REG_IP, 'gateway')
    DNS1 = (REG_IP, 'dns1')
    DNS2 = (REG_IP, 'dns2')
    ACTIVITY = (int, 'activity')

    SSH_KEY_ID_EXT = (REG_NUMBER, 'ssh_key_id')
    SSH_KEYS_ID = (list, 'ssh_keys_id')
    PUBLIC_KEY = (str, 'public_key')

    UUID = (str, 'uuid', (36, 36))
    NODE_ID = (str, 'node_id', (16, 16))
    UUIDS = (REG_UUIDS, 'uuids')
    AUTOSTART = (int, 'autostart')
    CPU = (int, 'cpu')
    MEMORY = (int, 'memory')
    OS_TEMPLATE_IMAGE_ID = (int, 'os_template_image_id')
    QUANTITY = (int, 'quantity')
    NAME = (str, 'name')
    PATH = (str, 'path')
    LOGIN_NAME = (str, 'login_name')
    PASSWORD = (str, 'password')
    LEASE_TERM = (int, 'lease_term')
    DESTINATION_HOST = (str, 'destination_host', (5, 64))
    DISK_UUID = (str, 'disk_uuid', (36, 36))
    DISK_SIZE = (int, 'size')
    DISK_SIZE_STR = (REG_NUMBER, 'size')
    IOPS = (int, 'iops')
    IOPS_RD = (int, 'iops_rd')
    IOPS_WR = (int, 'iops_wr')
    BPS = (int, 'bps')
    BPS_RD = (int, 'bps_rd')
    BPS_WR = (int, 'bps_wr')
    INFLUENCE_CURRENT_GUEST = (bool, 'influence_current_guest')

    GUEST_UUID = (str, 'guest_uuid', (36, 36))
    SNAPSHOT_ID = (str, 'snapshot_id', (10, 12))
    SNAPSHOTS_ID = (str, 'snapshots_id', (10, 1200))

    REMARK = (str, 'remark')
    USE_FOR = (int, 'use_for')
    LABEL = (str, 'label')
    DESCRIPTION = (str, 'description')
    OS_TYPE = (str, 'os_type')
    OS_DISTRO = (str, 'os_distro')
    OS_MAJOR = (int, 'os_major')
    OS_MINOR = (int, 'os_minor')
    OS_ARCH = (str, 'os_arch')
    OS_PRODUCT_NAME = (str, 'os_product_name')
    ACTIVE = (bool, 'active')
    ICON = (str, 'icon')
    LOGO = (str, 'logo')

    OS_TEMPLATE_IMAGE_KIND = (int, 'kind')
    OS_TEMPLATE_PROFILE_ID_EXT = (int, 'os_template_profile_id')
    OS_TEMPLATE_INITIALIZE_OPERATE_SET_ID_EXT = (int, 'os_template_initialize_operate_set_id')
    OS_TEMPLATE_INITIALIZE_OPERATE_KIND = (int, 'kind')
    OS_TEMPLATE_INITIALIZE_OPERATE_SEQUENCE = (int, 'sequence')
    OS_TEMPLATE_INITIALIZE_OPERATE_PATH = (str, 'path')
    OS_TEMPLATE_INITIALIZE_OPERATE_CONTENT = (str, 'content')
    OS_TEMPLATE_INITIALIZE_OPERATE_COMMAND = (str, 'command')

    OPERATE_RULE_KIND = (int, 'kind')
    OPERATE_RULE_SEQUENCE = (int, 'sequence')
    OPERATE_RULE_PATH = (str, 'path')
    OPERATE_RULE_CONTENT = (str, 'content')
    OPERATE_RULE_COMMAND = (str, 'command')

    TOKEN = (str, 'token')
    TOKENS = (str, 'tokens')

    PROJECT_ID = (int, 'project_id')
    PROJECTS_ID = (REG_NUMBERS, 'projects_id')
    SERVICE_ID = (int, 'service_id')
    SERVICE_ID_IN_URL = (REG_NUMBER, 'service_id')
    SERVICES_ID = (REG_NUMBERS, 'services_id')
