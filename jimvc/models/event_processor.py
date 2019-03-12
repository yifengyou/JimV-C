#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import json
import time
import jimit as ji

from jimvc.models import logger, app_config
from jimvc.models import Database as db, Config, GuestCPUMemory, GuestTraffic, GuestDiskIO, SSHKeyGuestMapping
from jimvc.models import Guest
from jimvc.models import Disk
from jimvc.models import Snapshot, SnapshotDiskMapping, OSTemplateImage
from jimvc.models import Log
from jimvc.models import Utils
from jimvc.models import EmitKind
from jimvc.models import ResponseState, GuestState, DiskState
from jimvc.models import GuestMigrateInfo
from jimvc.models import GuestCollectionPerformanceDataKind, HostCollectionPerformanceDataKind
from jimvc.models import HostCPUMemory, HostTraffic, HostDiskUsageIO


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
    snapshot = Snapshot()
    snapshot_disk_mapping = SnapshotDiskMapping()
    os_template_image = OSTemplateImage()
    config = Config()
    config.id = 1
    guest_cpu_memory = GuestCPUMemory()
    guest_traffic = GuestTraffic()
    guest_disk_io = GuestDiskIO()
    host_cpu_memory = HostCPUMemory()
    host_traffic = HostTraffic()
    host_disk_usage_io = HostDiskUsageIO()

    @classmethod
    def log_processor(cls):
        cls.log.set(type=cls.message['type'], timestamp=cls.message['timestamp'], host=cls.message['host'],
                    message=cls.message['message'],
                    full_message='' if cls.message['message'].__len__() < 255 else cls.message['message'])

        cls.log.create()
        pass

    @classmethod
    def guest_event_processor(cls):
        cls.guest.uuid = cls.message['message']['uuid']
        cls.guest.get_by('uuid')
        cls.guest.node_id = cls.message['node_id']
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

        elif cls.guest.status == GuestState.creating.value:
            if cls.message['message']['progress'] <= cls.guest.progress:
                return

            cls.guest.progress = cls.message['message']['progress']

        elif cls.guest.status == GuestState.snapshot_converting.value:
            cls.os_template_image.id = cls.message['message']['os_template_image_id']
            cls.os_template_image.get()

            if cls.message['message']['progress'] <= cls.os_template_image.progress:
                return

            cls.os_template_image.progress = cls.message['message']['progress']
            cls.os_template_image.update()
            return

        cls.guest.update()

        # 限定特殊情况下更新磁盘所属 Guest，避免迁移、创建时频繁被无意义的更新
        if cls.guest.status in [GuestState.running.value, GuestState.shutoff.value]:
            cls.disk.update_by_filter({'node_id': cls.guest.node_id}, filter_str='guest_uuid:eq:' + cls.guest.uuid)

    @classmethod
    def host_event_processor(cls):
        key = cls.message['message']['node_id']
        value = {
            'hostname': cls.message['host'],
            'cpu': cls.message['message']['cpu'],
            'cpuinfo': cls.message['message'].get('cpuinfo'),
            'system_load': cls.message['message']['system_load'],
            'memory': cls.message['message']['memory'],
            'memory_available': cls.message['message']['memory_available'],
            'dmidecode': cls.message['message']['dmidecode'],
            'interfaces': cls.message['message']['interfaces'],
            'disks': cls.message['message']['disks'],
            'boot_time': cls.message['message']['boot_time'],
            'nonrandom': False,
            'threads_status': cls.message['message']['threads_status'],
            'version': cls.message['message']['version'],
            'timestamp': ji.Common.ts()
        }

        db.r.hset(app_config['hosts_info'], key=key, value=json.dumps(value, ensure_ascii=False))

    @classmethod
    def response_processor(cls):
        _object = cls.message['message']['_object']
        action = cls.message['message']['action']
        uuid = cls.message['message']['uuid']
        state = cls.message['type']
        data = cls.message['message']['data']
        node_id = cls.message['node_id']

        if _object == 'guest':
            if action == 'create':
                if state == ResponseState.success.value:
                    # 系统盘的 UUID 与其 Guest 的 UUID 相同
                    cls.disk.uuid = uuid
                    cls.disk.get_by('uuid')
                    cls.disk.guest_uuid = uuid
                    cls.disk.state = DiskState.mounted.value
                    # disk_info['virtual-size'] 的单位为Byte，需要除以 1024 的 3 次方，换算成单位为 GB 的值
                    cls.disk.size = data['disk_info']['virtual-size'] / (1024 ** 3)
                    cls.disk.update()

                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.progress = 100
                    cls.guest.update()

                else:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.status = GuestState.dirty.value
                    cls.guest.update()

            elif action == 'migrate':
                pass

            elif action == 'sync_data':
                if state == ResponseState.success.value:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.autostart = bool(data['autostart'])
                    cls.guest.update()

            elif action == 'delete':
                if state == ResponseState.success.value:
                    cls.config.get()
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.delete()

                    # TODO: 加入是否删除使用的数据磁盘开关，如果为True，则顺便删除使用的磁盘。否则解除该磁盘被使用的状态。
                    cls.disk.uuid = uuid
                    cls.disk.get_by('uuid')
                    cls.disk.delete()
                    cls.disk.update_by_filter({'guest_uuid': '', 'sequence': -1, 'state': DiskState.idle.value},
                                              filter_str='guest_uuid:eq:' + cls.guest.uuid)

                    SSHKeyGuestMapping.delete_by_filter(filter_str=':'.join(['guest_uuid', 'eq', cls.guest.uuid]))

            elif action == 'reset_password':
                if state == ResponseState.success.value:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.password = cls.message['message']['passback_parameters']['password']
                    cls.guest.update()

            elif action == 'autostart':
                if state == ResponseState.success.value:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.autostart = cls.message['message']['passback_parameters']['autostart']
                    cls.guest.update()

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

            elif action == 'boot':

                if state == ResponseState.success.value:
                    pass

            elif action == 'allocate_bandwidth':
                if state == ResponseState.success.value:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.bandwidth = cls.message['message']['passback_parameters']['bandwidth']
                    cls.guest.update()

            elif action == 'adjust_ability':
                if state == ResponseState.success.value:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.cpu = cls.message['message']['passback_parameters']['cpu']
                    cls.guest.memory = cls.message['message']['passback_parameters']['memory']
                    cls.guest.update()

            elif action == 'change_vlan':
                if state == ResponseState.success.value:
                    cls.guest.uuid = uuid
                    cls.guest.get_by('uuid')
                    cls.guest.vlan_id = cls.message['message']['passback_parameters']['vlan_id']
                    cls.guest.update()

        elif _object == 'disk':
            if action == 'create':
                cls.disk.uuid = uuid
                cls.disk.get_by('uuid')
                cls.disk.node_id = node_id
                if state == ResponseState.success.value:
                    cls.disk.state = DiskState.idle.value

                else:
                    cls.disk.state = DiskState.dirty.value

                cls.disk.update()

            elif action == 'resize':
                if state == ResponseState.success.value:
                    cls.config.get()
                    cls.disk.uuid = uuid
                    cls.disk.get_by('uuid')
                    cls.disk.size = cls.message['message']['passback_parameters']['size']
                    cls.disk.quota(config=cls.config)
                    cls.disk.update()

            elif action == 'delete':
                cls.disk.uuid = uuid
                cls.disk.get_by('uuid')
                cls.disk.delete()

        elif _object == 'snapshot':
            if action == 'create':
                cls.snapshot.id = cls.message['message']['passback_parameters']['id']
                cls.snapshot.get()

                if state == ResponseState.success.value:
                    cls.snapshot.snapshot_id = data['snapshot_id']
                    cls.snapshot.parent_id = data['parent_id']
                    cls.snapshot.xml = data['xml']
                    cls.snapshot.progress = 100
                    cls.snapshot.update()

                    disks, _ = Disk.get_by_filter(filter_str='guest_uuid:eq:' + cls.snapshot.guest_uuid)

                    for disk in disks:
                        cls.snapshot_disk_mapping.snapshot_id = cls.snapshot.snapshot_id
                        cls.snapshot_disk_mapping.disk_uuid = disk['uuid']
                        cls.snapshot_disk_mapping.create()

                else:
                    cls.snapshot.progress = 255
                    cls.snapshot.update()

            if action == 'delete':
                if state == ResponseState.success.value:
                    cls.snapshot.id = cls.message['message']['passback_parameters']['id']
                    cls.snapshot.get()

                    # 更新子快照的 parent_id 为，当前快照的 parent_id。因为当前快照已被删除。
                    Snapshot.update_by_filter({'parent_id': cls.snapshot.parent_id},
                                              filter_str='parent_id:eq:' + cls.snapshot.snapshot_id)

                    SnapshotDiskMapping.delete_by_filter(
                        filter_str=':'.join(['snapshot_id', 'eq', cls.snapshot.snapshot_id]))

                    cls.snapshot.delete()

                else:
                    pass

            if action == 'revert':
                # 不论恢复成功与否，都使快照恢复至正常状态。
                cls.snapshot.id = cls.message['message']['passback_parameters']['id']
                cls.snapshot.get()
                cls.snapshot.progress = 100
                cls.snapshot.update()

            if action == 'convert':
                cls.snapshot.snapshot_id = cls.message['message']['passback_parameters']['id']
                cls.snapshot.get_by('snapshot_id')
                cls.snapshot.progress = 100
                cls.snapshot.update()

                cls.os_template_image.id = cls.message['message']['passback_parameters']['os_template_image_id']
                cls.os_template_image.get()

                if state == ResponseState.success.value:
                    cls.os_template_image.progress = 100

                else:
                    cls.os_template_image.progress = 255

                cls.os_template_image.update()

        elif _object == 'os_template_image':
            if action == 'delete':
                cls.os_template_image.id = cls.message['message']['passback_parameters']['id']
                cls.os_template_image.get()

                if state == ResponseState.success.value:
                    cls.os_template_image.delete()

                else:
                    pass

        else:
            pass

    @classmethod
    def guest_collection_performance_processor(cls):
        data_kind = cls.message['type']
        timestamp = ji.Common.ts()
        timestamp -= (timestamp % 60)
        data = cls.message['message']['data']

        if data_kind == GuestCollectionPerformanceDataKind.cpu_memory.value:
            for item in data:
                cls.guest_cpu_memory.guest_uuid = item['guest_uuid']
                cls.guest_cpu_memory.cpu_load = item['cpu_load']
                cls.guest_cpu_memory.memory_available = item['memory_available']
                cls.guest_cpu_memory.memory_rate = item['memory_rate']
                cls.guest_cpu_memory.timestamp = timestamp
                cls.guest_cpu_memory.create()

        if data_kind == GuestCollectionPerformanceDataKind.traffic.value:
            for item in data:
                cls.guest_traffic.guest_uuid = item['guest_uuid']
                cls.guest_traffic.name = item['name']
                cls.guest_traffic.rx_bytes = item['rx_bytes']
                cls.guest_traffic.rx_packets = item['rx_packets']
                cls.guest_traffic.rx_errs = item['rx_errs']
                cls.guest_traffic.rx_drop = item['rx_drop']
                cls.guest_traffic.tx_bytes = item['tx_bytes']
                cls.guest_traffic.tx_packets = item['tx_packets']
                cls.guest_traffic.tx_errs = item['tx_errs']
                cls.guest_traffic.tx_drop = item['tx_drop']
                cls.guest_traffic.timestamp = timestamp
                cls.guest_traffic.create()

        if data_kind == GuestCollectionPerformanceDataKind.disk_io.value:
            for item in data:
                cls.guest_disk_io.disk_uuid = item['disk_uuid']
                cls.guest_disk_io.rd_req = item['rd_req']
                cls.guest_disk_io.rd_bytes = item['rd_bytes']
                cls.guest_disk_io.wr_req = item['wr_req']
                cls.guest_disk_io.wr_bytes = item['wr_bytes']
                cls.guest_disk_io.timestamp = timestamp
                cls.guest_disk_io.create()

        else:
            pass

    @classmethod
    def host_collection_performance_processor(cls):
        data_kind = cls.message['type']
        timestamp = ji.Common.ts()
        timestamp -= (timestamp % 60)
        data = cls.message['message']['data']

        if data_kind == HostCollectionPerformanceDataKind.cpu_memory.value:
            cls.host_cpu_memory.node_id = data['node_id']
            cls.host_cpu_memory.cpu_load = data['cpu_load']
            cls.host_cpu_memory.memory_available = data['memory_available']
            cls.host_cpu_memory.timestamp = timestamp
            cls.host_cpu_memory.create()

        if data_kind == HostCollectionPerformanceDataKind.traffic.value:
            for item in data:
                cls.host_traffic.node_id = item['node_id']
                cls.host_traffic.name = item['name']
                cls.host_traffic.rx_bytes = item['rx_bytes']
                cls.host_traffic.rx_packets = item['rx_packets']
                cls.host_traffic.rx_errs = item['rx_errs']
                cls.host_traffic.rx_drop = item['rx_drop']
                cls.host_traffic.tx_bytes = item['tx_bytes']
                cls.host_traffic.tx_packets = item['tx_packets']
                cls.host_traffic.tx_errs = item['tx_errs']
                cls.host_traffic.tx_drop = item['tx_drop']
                cls.host_traffic.timestamp = timestamp
                cls.host_traffic.create()

        if data_kind == HostCollectionPerformanceDataKind.disk_usage_io.value:
            for item in data:
                cls.host_disk_usage_io.node_id = item['node_id']
                cls.host_disk_usage_io.mountpoint = item['mountpoint']
                cls.host_disk_usage_io.used = item['used']
                cls.host_disk_usage_io.rd_req = item['rd_req']
                cls.host_disk_usage_io.rd_bytes = item['rd_bytes']
                cls.host_disk_usage_io.wr_req = item['wr_req']
                cls.host_disk_usage_io.wr_bytes = item['wr_bytes']
                cls.host_disk_usage_io.timestamp = timestamp
                cls.host_disk_usage_io.create()

        else:
            pass

    @classmethod
    def launch(cls):
        logger.info(msg='Thread EventProcessor is launched.')
        while True:
            if Utils.exit_flag:
                msg = 'Thread EventProcessor say bye-bye'
                print msg
                logger.info(msg=msg)

                return

            try:
                report = db.r.lpop(app_config['upstream_queue'])

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

                elif cls.message['kind'] == EmitKind.guest_collection_performance.value:
                    cls.guest_collection_performance_processor()

                elif cls.message['kind'] == EmitKind.host_collection_performance.value:
                    cls.host_collection_performance_processor()

                else:
                    pass

            except AttributeError as e:
                logger.error(traceback.format_exc())
                time.sleep(1)

                if db.r is None:
                    db.init_conn_redis()

            except Exception as e:
                logger.error(traceback.format_exc())
                time.sleep(1)

