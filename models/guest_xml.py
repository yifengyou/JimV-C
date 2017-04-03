#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import Config
from models import Guest


__author__ = 'James Iter'
__date__ = '2017/3/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


class GuestXML(object):
    """
    <?xml version="1.0" encoding="utf-8"?>
    <domain type="kvm">
      <features>
        <acpi/>
        <apic/>
      </features>
      <name>10v022</name>
      <vcpu>16</vcpu>
      <memory unit="GiB">64</memory>
      <os>
        <boot dev="hd"/>
        <type arch="x86_64">hvm</type>
        <bootmenu timeout="3000" enable="yes"/>
      </os>
      <devices>
        <interface type='network'>
          <source network='net-br0'/>
          <model type='virtio'/>
        </interface>
        <disk type='network' device='disk'>
            <driver name='qemu' type='qcow2' cache='none'/>
            <source protocol='gluster' name='gv0/VMs/disk_pool/10v01251/L_10v01251.qcow2'>
                <host name='127.0.0.1' port='24007'/>
            </source>
            <target dev='vda' bus='virtio'/>
        </disk>
        <graphics passwd="000000" keymap="en-us" port="6002" type="vnc">
          <listen network="net-br0" type="network"/>
        </graphics>
        <serial type='pty'>
            <target port='0'/>
        </serial>
        <console type='pty'>
            <target type='serial' port='0'/>
        </console>
      </devices>
    </domain>
    """

    def __init__(self, guest=None, disks=None, config=None):
        assert isinstance(guest, Guest)
        assert isinstance(disks, list)
        assert isinstance(config, Config)

        self.guest = guest
        self.disks = disks
        self.config = config

    def get_domain(self):
        return """
            <?xml version="1.0" encoding="utf-8"?>
            <domain type="kvm">
            {0}
            {1}
            {2}
            {3}
            {4}
            {5}
            </domain>
        """.format(self.get_features(), self.get_name(), self.get_vcpu(), self.get_memory(), self.get_os(),
                   self.get_devices())

    @staticmethod
    def get_features():
        return """
            <features>
                <acpi/>
                <apic/>
            </features>
        """

    def get_name(self):
        return """<name>{0}</name>""".format(self.guest.name)

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
            </devices>
        """.format(self.get_interface(), self.get_disks(), self.get_graphics(), self.get_console())

    def get_interface(self):
        return """
            <interface type='network'>
                <source network='{0}'/>
                <model type='virtio'/>
            </interface>
        """.format(self.guest.network)

    def get_disks(self):

        disks = []
        dev_table = ['vda', 'vdb', 'vdc', 'vdd']

        for i, disk in enumerate(self.disks):
            disks.append("""
                <disk type='network' device='disk'>
                    <driver name='qemu' type='qcow2' cache='none'/>
                    <source protocol='gluster' name='{0}/VMs/{1}/{2}.{3}'>
                        <host name='127.0.0.1' port='24007'/>
                    </source>
                    <target dev='{4}' bus='virtio'/>
                </disk>
            """.format(self.config.glusterfs_volume, self.guest.name, disk['label'], disk['format'], dev_table[i]))

        return ''.join(disks)

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

