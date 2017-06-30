#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import time
from IPy import IP
import jimit as ji

from models import Database as db, Config, CPUMemory, Traffic, DiskIO
from models import Guest
from models import Disk
from models import Log
from models import Utils
from models import EmitKind
from models import ResponseState, GuestState, DiskState
from models.guest import GuestMigrateInfo
from models.initialize import app, logger
from models.status import CollectionPerformanceDataKind


__author__ = 'James Iter'
__date__ = '2017/4/15'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class EventProcessor(object):
    message = None
    log = Log()
    guest = Guest()
    guest_migrate_info = GuestMigrateInfo()
    disk = Disk()
    config = Config()
    cpu_memory = CPUMemory()
    traffic = Traffic()
    disk_io = DiskIO()

    @classmethod
    def log_processor(cls):
        cls.log.set(type=cls.message['type'], timestamp=cls.message['timestamp'], host=cls.message['host'],
                    message=cls.message['message'])

        cls.log.create()

    @classmethod
    def guest_event_processor(cls):
        cls.guest.uuid = cls.message['message']['uuid']
        cls.guest.get_by('uuid')
        cls.guest.on_host = cls.message['host']
        last_status = cls.guest.status
        cls.guest.status = cls.message['type']

        if cls.message['type'] == GuestState.update.value:
            # 更新事件不改变 Guest 的状态
            cls.guest.status = last_status
            cls.guest.xml = cls.message['message']['xml']

        elif cls.guest.status == GuestState.migrating.value:
            try:
                cls.guest_migrate_info.uuid = cls.guest.uuid
                cls.guest_migrate_info.get_by('uuid')

                cls.guest_migrate_info.type = cls.message['message']['migrating_info']['type']
                cls.guest_migrate_info.time_elapsed = cls.message['message']['migrating_info']['time_elapsed']
                cls.guest_migrate_info.time_remaining = cls.message['message']['migrating_info']['time_remaining']
                cls.guest_migrate_info.data_total = cls.message['message']['migrating_info']['data_total']
                cls.guest_migrate_info.data_processed = cls.message['message']['migrating_info']['data_processed']
                cls.guest_migrate_info.data_remaining = cls.message['message']['migrating_info']['data_remaining']
                cls.guest_migrate_info.mem_total = cls.message['message']['migrating_info']['mem_total']
                cls.guest_migrate_info.mem_processed = cls.message['message']['migrating_info']['mem_processed']
                cls.guest_migrate_info.mem_remaining = cls.message['message']['migrating_info']['mem_remaining']
                cls.guest_migrate_info.file_total = cls.message['message']['migrating_info']['file_total']
                cls.guest_migrate_info.file_processed = cls.message['message']['migrating_info']['file_processed']
                cls.guest_migrate_info.file_remaining = cls.message['message']['migrating_info']['file_remaining']

                cls.guest_migrate_info.update()

            except ji.PreviewingError as e:
                ret = json.loads(e.message)
                if ret['state']['code'] == '404':
                    cls.guest_migrate_info.type = cls.message['message']['migrating_info']['type']
                    cls.guest_migrate_info.time_elapsed = cls.message['message']['migrating_info']['time_elapsed']
                    cls.guest_migrate_info.time_remaining = cls.message['message']['migrating_info']['time_remaining']
                    cls.guest_migrate_info.data_total = cls.message['message']['migrating_info']['data_total']
                    cls.guest_migrate_info.data_processed = cls.message['message']['migrating_info']['data_processed']
                    cls.guest_migrate_info.data_remaining = cls.message['message']['migrating_info']['data_remaining']
                    cls.guest_migrate_info.mem_total = cls.message['message']['migrating_info']['mem_total']
                    cls.guest_migrate_info.mem_processed = cls.message['message']['migrating_info']['mem_processed']
                    cls.guest_migrate_info.mem_remaining = cls.message['message']['migrating_info']['mem_remaining']
                    cls.guest_migrate_info.file_total = cls.message['message']['migrating_info']['file_total']
                    cls.guest_migrate_info.file_processed = cls.message['message']['migrating_info']['file_processed']
                    cls.guest_migrate_info.file_remaining = cls.message['message']['migrating_info']['file_remaining']

                    cls.guest_migrate_info.create()

        cls.guest.update()

    @classmethod
    def host_event_processor(cls):
        key = cls.message['message']['node_id']
        value = {
            'hostname': cls.message['host'],
            'timestamp': ji.Common.ts()
        }

        db.r.hset(app.config['hosts_info'], key=key, value=json.dumps(value, ensure_ascii=False))
        db.r.expire(app.config['hosts_info'], 10)

    @classmethod
    def response_processor(cls):
        action = cls.message['message']['action']
        uuid = cls.message['message']['uuid']
        state = cls.message['type']
        data = cls.message['message']['data']

        if action == 'create_guest':
            if state == ResponseState.success.value:
                # 系统盘的 UUID 与其 Guest 的 UUID 相同
                cls.disk.uuid = uuid
                cls.disk.get_by('uuid')
                cls.disk.guest_uuid = uuid
                cls.disk.state = DiskState.mounted.value
                # disk_info['virtual-size'] 的单位为Byte，需要除以 1024 的 3 次方，换算成单位为 GB 的值
                cls.disk.size = data['disk_info']['virtual-size'] / (1024 ** 3)
                cls.disk.update()

            else:
                cls.guest.uuid = uuid
                cls.guest.get_by('uuid')
                cls.guest.status = GuestState.dirty.value
                cls.guest.update()

        elif action == 'migrate':
            pass

        elif action == 'delete_guest':
            if state == ResponseState.success.value:
                cls.config.id = 1
                cls.config.get()
                cls.guest.uuid = uuid
                cls.guest.get_by('uuid')

                if IP(cls.config.start_ip).int() <= IP(cls.guest.ip).int() <= IP(cls.config.end_ip).int():
                    if db.r.srem(app.config['ip_used_set'], cls.guest.ip):
                        db.r.sadd(app.config['ip_available_set'], cls.guest.ip)

                if (cls.guest.vnc_port - cls.config.start_vnc_port) <= \
                        (IP(cls.config.end_ip).int() - IP(cls.config.start_ip).int()):
                    if db.r.srem(app.config['vnc_port_used_set'], cls.guest.vnc_port):
                        db.r.sadd(app.config['vnc_port_available_set'], cls.guest.vnc_port)

                cls.guest.delete()

                cls.disk.uuid = uuid
                cls.disk.get_by('uuid')
                cls.disk.delete()

        elif action == 'create_disk':
            cls.disk.uuid = uuid
            cls.disk.get_by('uuid')
            if state == ResponseState.success.value:
                cls.disk.state = DiskState.idle.value

            else:
                cls.disk.state = DiskState.dirty.value

            cls.disk.update()

        elif action == 'resize_disk':
            if state == ResponseState.success.value:
                cls.disk.uuid = uuid
                cls.disk.get_by('uuid')
                cls.disk.size = cls.message['message']['passback_parameters']['size']
                cls.disk.update()

        elif action == 'attach_disk':
            cls.disk.uuid = cls.message['message']['passback_parameters']['disk_uuid']
            cls.disk.get_by('uuid')
            if state == ResponseState.success.value:
                cls.disk.guest_uuid = uuid
                cls.disk.sequence = cls.message['message']['passback_parameters']['sequence']
                cls.disk.state = DiskState.mounted.value
                cls.disk.update()

        elif action == 'detach_disk':
            cls.disk.uuid = cls.message['message']['passback_parameters']['disk_uuid']
            cls.disk.get_by('uuid')
            if state == ResponseState.success.value:
                cls.disk.guest_uuid = ''
                cls.disk.sequence = -1
                cls.disk.state = DiskState.idle.value
                cls.disk.update()

        elif action == 'delete_disk':
            cls.disk.uuid = uuid
            cls.disk.get_by('uuid')
            cls.disk.delete()

        elif action == 'boot':
            boot_jobs_id = cls.message['message']['passback_parameters']['boot_jobs_id']

            if state == ResponseState.success.value:
                cls.guest.uuid = uuid
                cls.guest.delete_boot_jobs(boot_jobs_id=boot_jobs_id)

        else:
            pass

    @classmethod
    def collection_performance_processor(cls):
        data_kind = cls.message['type']
        timestamp = cls.message['timestamp']
        data = cls.message['message']['data']

        if data_kind == CollectionPerformanceDataKind.cpu_memory.value:
            for item in data:
                cls.cpu_memory.guest_uuid = item['guest_uuid']
                cls.cpu_memory.cpu_load = item['cpu_load']
                cls.cpu_memory.memory_available = item['memory_available']
                cls.cpu_memory.memory_unused = item['memory_unused']
                cls.cpu_memory.timestamp = timestamp
                cls.cpu_memory.create()

        if data_kind == CollectionPerformanceDataKind.traffic.value:
            for item in data:
                cls.traffic.guest_uuid = item['guest_uuid']
                cls.traffic.name = item['name']
                cls.traffic.rx_bytes = item['rx_bytes']
                cls.traffic.rx_packets = item['rx_packets']
                cls.traffic.rx_errs = item['rx_errs']
                cls.traffic.rx_drop = item['rx_drop']
                cls.traffic.tx_bytes = item['tx_bytes']
                cls.traffic.tx_packets = item['tx_packets']
                cls.traffic.tx_errs = item['tx_errs']
                cls.traffic.tx_drop = item['tx_drop']
                cls.traffic.timestamp = timestamp
                cls.traffic.create()

        if data_kind == CollectionPerformanceDataKind.disk_io.value:
            for item in data:
                cls.disk_io.disk_uuid = item['disk_uuid']
                cls.disk_io.rd_req = item['rd_req']
                cls.disk_io.rd_bytes = item['rd_bytes']
                cls.disk_io.wr_req = item['wr_req']
                cls.disk_io.wr_bytes = item['wr_bytes']
                cls.disk_io.timestamp = timestamp
                cls.disk_io.create()

        else:
            pass

    @classmethod
    def launch(cls):
        while True:
            if Utils.exit_flag:
                Utils.thread_counter -= 1
                print 'Thread EventProcessor say bye-bye'
                return

            try:
                report = db.r.lpop(app.config['upstream_queue'])

                if report is None:
                    time.sleep(1)
                    continue

                cls.message = json.loads(report)

                if cls.message['kind'] == EmitKind.log.value:
                    cls.log_processor()

                elif cls.message['kind'] == EmitKind.guest_event.value:
                    cls.guest_event_processor()

                elif cls.message['kind'] == EmitKind.host_event.value:
                    cls.host_event_processor()

                elif cls.message['kind'] == EmitKind.response.value:
                    cls.response_processor()

                elif cls.message['kind'] == EmitKind.collection_performance.value:
                    cls.collection_performance_processor()

                else:
                    pass

            except Exception as e:
                logger.error(e.message)

