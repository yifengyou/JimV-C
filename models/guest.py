#!/usr/bin/env python
# -*- coding: utf-8 -*-


import jimit as ji
import json

from filter import FilterFieldType
from orm import ORM
from status import GuestState, DiskState
from database import Database as db
from initialize import app


__author__ = 'James Iter'
__date__ = '2017/3/22'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class Guest(ORM):

    _table_name = 'guest'
    _primary_key = 'id'

    def __init__(self):
        super(Guest, self).__init__()
        self.id = 0
        self.uuid = None
        self.label = None
        self.password = None
        self.remark = ''
        self.os_template_id = None
        self.create_time = ji.Common.tus()
        self.status = GuestState.no_state.value
        self.progress = 0
        self.on_host = ''
        self.cpu = None
        self.memory = None
        self.ip = None
        self.network = None
        self.manage_network = None
        self.vnc_port = None
        self.vnc_password = None
        self.xml = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'uuid': FilterFieldType.STR.value,
            'label': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value,
            'on_host': FilterFieldType.STR.value,
            'ip': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['remark', 'cpu', 'memory', 'network', 'manage_network', 'vnc_password']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['label', 'remark', 'on_host', 'ip']

    @staticmethod
    def emit_instruction(message):
        db.r.publish(app.config['instruction_channel'], message=message)

    def get_boot_jobs_key(self):
        return ':'.join([app.config['guest_boot_jobs'], self.uuid])

    def add_boot_jobs(self, boot_jobs_id):
        if not isinstance(boot_jobs_id, list):
            raise

        key = self.get_boot_jobs_key()
        db.r.sadd(key, *boot_jobs_id)
        db.r.expire(key, app.config['guest_boot_jobs_wait_time'])

    def get_boot_jobs(self):
        return db.r.ttl(self.get_boot_jobs_key()), list(db.r.smembers(self.get_boot_jobs_key()))

    def delete_boot_jobs(self, boot_jobs_id):
        if not isinstance(boot_jobs_id, list):
            raise

        key = self.get_boot_jobs_key()
        db.r.srem(key, *boot_jobs_id)

        # 如果集合下还有值，则更新启动作业有效时间
        if db.r.exists(key):
            db.r.expire(key, app.config['guest_boot_jobs_wait_time'])

    @staticmethod
    def get_uuids_of_all_had_boot_job():
        boot_job_keys = db.r.keys(pattern=app.config['guest_boot_jobs'] + '*')
        uuids = list()
        for boot_job_key in boot_job_keys:
            uuids.append(boot_job_key.split(':')[-1])

        return uuids

    @staticmethod
    def get_lightest_host():
        # 负载最小的宿主机
        lightest_host = None
        for k, v in db.r.hgetall(app.config['hosts_info']).items():
            v = json.loads(v)

            if lightest_host is None:
                lightest_host = v

            if float(lightest_host['system_load'][0]) / lightest_host['cpu'] > \
                    float(v['system_load'][0]) / v['cpu']:
                lightest_host = v

        return lightest_host

    @staticmethod
    def get_available_hosts():

        from models import Host

        hosts = list()

        for k, v in db.r.hgetall(app.config['hosts_info']).items():
            v = json.loads(v)

            v = Host.alive_check(v)

            if not v['alive']:
                continue

            v['system_load_per_cpu'] = float(v['system_load'][0]) / v['cpu']
            hosts.append(v)

        hosts.sort(key=lambda _k: _k['system_load_per_cpu'])

        return hosts


class Disk(ORM):

    _table_name = 'disk'
    _primary_key = 'id'

    def __init__(self):
        super(Disk, self).__init__()
        self.id = 0
        self.uuid = None
        self.remark = None
        self.path = None
        self.size = None
        self.sequence = None
        self.state = DiskState.pending.value
        self.on_host = ''
        self.format = 'qcow2'
        self.create_time = ji.Common.tus()
        self.guest_uuid = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'uuid': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value,
            'size': FilterFieldType.INT.value,
            'state': FilterFieldType.INT.value,
            'sequence': FilterFieldType.INT.value,
            'on_host': FilterFieldType.STR.value,
            'guest_uuid': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return ['on_host', 'sequence', 'state', 'guest_uuid']

    @staticmethod
    def get_allow_content_search_keywords():
        return ['remark', 'size', 'guest_uuid', 'uuid', 'on_host']


class GuestMigrateInfo(ORM):

    _table_name = 'guest_migrate_info'
    _primary_key = 'id'

    def __init__(self):
        super(GuestMigrateInfo, self).__init__()
        self.id = 0
        self.uuid = None
        self.type = None
        self.time_elapsed = None
        self.time_remaining = None
        self.data_total = None
        self.data_processed = None
        self.data_remaining = None
        self.mem_total = None
        self.mem_processed = None
        self.mem_remaining = None
        self.file_total = None
        self.file_processed = None
        self.file_remaining = None

    @staticmethod
    def get_filter_keywords():
        return {
            'id': FilterFieldType.INT.value,
            'uuid': FilterFieldType.STR.value
        }

    @staticmethod
    def get_allow_update_keywords():
        return []

    @staticmethod
    def get_allow_content_search_keywords():
        return []

