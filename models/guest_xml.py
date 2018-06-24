#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models import Config, Disk
from models import Guest
from models import status


__author__ = 'James Iter'
__date__ = '2017/3/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class GuestXML(object):

    def __init__(self, guest=None, disk=None, config=None, os_type=None):
        assert isinstance(guest, Guest)
        assert isinstance(disk, Disk)
        assert isinstance(config, Config)

        self.guest = guest
        self.disk = disk
        self.config = config
        self.os_type = os_type

    def get_domain(self):
        return """<?xml version="1.0" encoding="utf-8"?>
            <domain type="kvm">
            {0}
            {1}
            {2}
            {3}
            {4}
            {5}
            {6}
            {7}
            {8}
            </domain>
        """.format(self.get_features(), self.get_cpu_mode(), self.get_clock(), self.get_name(), self.get_uuid(),
                   self.get_vcpu(), self.get_memory(), self.get_os(), self.get_devices())

    @staticmethod
    def get_features():
        return """
            <features>
                <acpi/>
                <apic/>
            </features>
        """

    @staticmethod
    def get_cpu_mode():
        return """<cpu mode='host-passthrough'/>"""

    def get_clock(self):
        # clock 参考链接：https://libvirt.org/formatdomain.html#elementsTime
        # Windows Guest 设为 localtime，非 Windows Guest 都设为 utc
        offset = 'utc'

        if str(self.os_type).lower().find('windows') >= 0:
            offset = 'localtime'

        return """<clock offset='{0}'/>""".format(offset)

    def get_name(self):
        return """<name>{0}</name>""".format(self.guest.label)

    def get_uuid(self):
        return """<uuid>{0}</uuid>""".format(self.guest.uuid)

    def get_vcpu(self):
        return """<vcpu>{0}</vcpu>""".format(self.guest.cpu.__str__())

    def get_memory(self):
        return """<memory unit="GiB">{0}</memory>""".format(self.guest.memory.__str__())

    @staticmethod
    def get_os():
        return """
            <os>
                <boot dev="hd"/>
                <type arch="x86_64">hvm</type>
                <bootmenu timeout="3000" enable="yes"/>
            </os>
        """

    def get_devices(self):
        return """
            <devices>
                {0}
                {1}
                {2}
                {3}
                {4}
            </devices>
        """.format(self.get_interface(), self.get_disk(), self.get_graphics(), self.get_console(), self.get_channel())

    def get_interface(self):
        return """
            <interface type='network'>
                <source network='{0}'/>
                <model type='virtio'/>
                <bandwidth>
                    <inbound average='{1}'/>
                    <outbound average='{1}'/>
                </bandwidth>
            </interface>
        """.format(self.guest.network, self.guest.bandwidth / 1000 / 8)

    def get_disk(self):

        from initialize import dev_table

        if self.config.storage_mode in [status.StorageMode.local.value, status.StorageMode.shared_mount.value]:
            disk_xml = """
                <disk type='file' device='disk'>
                    <driver name='qemu' type='{0}' cache='none'/>
                    <source file='{1}'/>
                    <target dev='{2}' bus='virtio'/>
                </disk>
            """.format(self.disk.format, self.disk.path, dev_table[self.disk.sequence])

        elif self.config.storage_mode in [status.StorageMode.ceph.value, status.StorageMode.glusterfs.value]:
            dfs_protocol = 'ceph'

            if self.config.storage_mode == status.StorageMode.glusterfs.value:
                dfs_protocol = 'gluster'

            disk_xml = """
                <disk type='network' device='disk'>
                    <driver name='qemu' type='{0}' cache='none'/>
                    <source protocol='{1}' name='{2}/{3}'>
                        <host name='127.0.0.1' port='24007'/>
                    </source>
                    <target dev='{4}' bus='virtio'/>
                </disk>
            """.format(self.disk.format, dfs_protocol, self.config.dfs_volume, self.disk.path,
                       dev_table[self.disk.sequence])

        else:
            disk_xml = ''

        return disk_xml

    def get_graphics(self):
        return """
            <graphics passwd="{0}" keymap="en-us" port="{1}" type="vnc">
                <listen network="{2}" type="network"/>
            </graphics>
        """.format(self.guest.vnc_password, self.guest.vnc_port, self.guest.manage_network)

    @staticmethod
    def get_console():
        return """
            <serial type='pty'>
                <target port='0'/>
            </serial>
            <console type='pty'>
                <target type='serial' port='0'/>
            </console>
        """

    @staticmethod
    def get_channel():
        return """
            <channel type='unix'>
                <source mode='bind'/>
                <target type='virtio' name='org.qemu.guest_agent.0'/>
            </channel>
        """

