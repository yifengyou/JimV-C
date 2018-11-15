-- DROP DATABASE IF EXISTS jimv;
CREATE DATABASE IF NOT EXISTS jimv CHARACTER SET utf8;
USE jimv;


CREATE TABLE IF NOT EXISTS user(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_name VARCHAR(30) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    create_time BIGINT UNSIGNED NOT NULL,
    mobile_phone VARCHAR(13) NOT NULL DEFAULT '',
    email VARCHAR(30) NOT NULL DEFAULT '',
    mobile_phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    role_id BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE user ADD INDEX (login_name);
ALTER TABLE user ADD INDEX (mobile_phone);
ALTER TABLE user ADD INDEX (email);
INSERT INTO user (login_name, password, create_time) VALUES
    ('admin', 'ji_pbkdf2$sha1$1000$b8UzawEs5kJ68TmbqQEqD07jgZGCYJsa$d3593420edee742499a974f2f377e5b220927dc7', UNIX_TIMESTAMP(NOW()) * 1000000);
# password jimv.pswd.com


CREATE TABLE IF NOT EXISTS guest(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    label VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    remark VARCHAR(255) NOT NULL DEFAULT '',
    os_template_image_id BIGINT UNSIGNED NOT NULL,
    create_time BIGINT UNSIGNED NOT NULL,
    -- 运行时的状态用 status;
    -- state倾向于condition，是一种延续性的状态。status常用于描述一个过程中的某阶段
    status TINYINT UNSIGNED NOT NULL DEFAULT 0,
    progress TINYINT UNSIGNED NOT NULL DEFAULT 0,
    node_id BIGINT UNSIGNED NOT NULL,
    service_id BIGINT UNSIGNED NOT NULL default 1,
    cpu TINYINT UNSIGNED NOT NULL,
    memory INT UNSIGNED NOT NULL,
    -- bps
    bandwidth INT UNSIGNED NOT NULL DEFAULT 0,
    ip CHAR(15) NOT NULL,
    network VARCHAR(64) NOT NULL,
    manage_network VARCHAR(64) NOT NULL,
    vnc_port INT UNSIGNED NOT NULL,
    vnc_password VARCHAR(255) NOT NULL,
    xml TEXT NOT NULL,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE guest ADD INDEX (uuid);
ALTER TABLE guest ADD INDEX (label);
ALTER TABLE guest ADD INDEX (node_id);
ALTER TABLE guest ADD INDEX (service_id);
ALTER TABLE guest ADD INDEX (ip);
ALTER TABLE guest ADD INDEX (remark);


CREATE TABLE IF NOT EXISTS guest_migrate_info(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    type TINYINT UNSIGNED NOT NULL DEFAULT 0,
    time_elapsed BIGINT UNSIGNED NOT NULL DEFAULT 0,
    time_remaining BIGINT UNSIGNED NOT NULL DEFAULT 0,
    data_total BIGINT UNSIGNED NOT NULL DEFAULT 0,
    data_processed BIGINT UNSIGNED NOT NULL DEFAULT 0,
    data_remaining BIGINT UNSIGNED NOT NULL DEFAULT 0,
    mem_total BIGINT UNSIGNED NOT NULL DEFAULT 0,
    mem_processed BIGINT UNSIGNED NOT NULL DEFAULT 0,
    mem_remaining BIGINT UNSIGNED NOT NULL DEFAULT 0,
    file_total BIGINT UNSIGNED NOT NULL DEFAULT 0,
    file_processed BIGINT UNSIGNED NOT NULL DEFAULT 0,
    file_remaining BIGINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE guest_migrate_info ADD INDEX (uuid);


CREATE TABLE IF NOT EXISTS disk(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    path VARCHAR(255) NOT NULL,
    size INT UNSIGNED NOT NULL,
    node_id BIGINT UNSIGNED NOT NULL,
    remark VARCHAR(255) NOT NULL DEFAULT '',
    sequence TINYINT NOT NULL,
    format CHAR(16) NOT NULL DEFAULT 'qcow2',
    -- 实例固有的状态用 state;
    state TINYINT UNSIGNED NOT NULL DEFAULT 0,
    create_time BIGINT UNSIGNED NOT NULL,
    guest_uuid CHAR(36) NOT NULL,
    iops BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_rd BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_wr BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_max BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_rd BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_wr BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_max BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE disk ADD INDEX (size);
ALTER TABLE disk ADD INDEX (guest_uuid);
ALTER TABLE disk ADD INDEX (node_id);
ALTER TABLE disk ADD INDEX (remark);


-- 操作系统模板镜像
CREATE TABLE IF NOT EXISTS os_template_image(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    path VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    logo VARCHAR(255) NOT NULL,
    os_template_profile_id BIGINT UNSIGNED NOT NULL,
    kind TINYINT UNSIGNED NOT NULL DEFAULT 0,
    progress TINYINT UNSIGNED NOT NULL DEFAULT 0,
    create_time BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;


-- 操作系统模板描述文件
CREATE TABLE IF NOT EXISTS os_template_profile(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    -- http://libguestfs.org/guestfish.1.html#inspect-get-type
    os_type VARCHAR(10) NOT NULL,
    -- http://libguestfs.org/guestfish.1.html#inspect-get-distro
    os_distro VARCHAR(20) NOT NULL,
    os_major TINYINT UNSIGNED NOT NULL,
    os_minor TINYINT UNSIGNED NOT NULL,
    -- http://libguestfs.org/guestfish.1.html#inspect-get-arch  http://libguestfs.org/guestfish.1.html#file-architecture
    os_arch VARCHAR(10) NOT NULL,
    os_product_name VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    icon VARCHAR(255) NOT NULL,
    os_template_initialize_operate_set_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE os_template_profile ADD INDEX (label);
ALTER TABLE os_template_profile ADD INDEX (os_type);
ALTER TABLE os_template_profile ADD INDEX (os_distro);
ALTER TABLE os_template_profile ADD INDEX (os_product_name);


-- 操作系统模板初始化操作集
CREATE TABLE IF NOT EXISTS os_template_initialize_operate_set(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE os_template_initialize_operate_set ADD INDEX (label);


-- 操作系统模板初始化操作细则
CREATE TABLE IF NOT EXISTS os_template_initialize_operate(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    os_template_initialize_operate_set_id BIGINT UNSIGNED NOT NULL,
    kind TINYINT UNSIGNED NOT NULL DEFAULT 0,
    sequence TINYINT UNSIGNED NOT NULL DEFAULT 0,
    path VARCHAR(255) NOT NULL,
    content TEXT,
    command TEXT,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE os_template_initialize_operate ADD INDEX (os_template_initialize_operate_set_id);


CREATE TABLE IF NOT EXISTS config(
    id BIGINT UNSIGNED NOT NULL DEFAULT 1,
    jimv_edition TINYINT UNSIGNED NOT NULL DEFAULT 0,
    storage_mode TINYINT UNSIGNED NOT NULL DEFAULT 0,
    dfs_volume VARCHAR(255) NOT NULL DEFAULT '',
    storage_path VARCHAR(255) NOT NULL,
    vm_network VARCHAR(255) NOT NULL,
    vm_manage_network VARCHAR(255) NOT NULL,
    start_ip CHAR(15) NOT NULL,
    end_ip CHAR(15) NOT NULL,
    start_vnc_port INT UNSIGNED NOT NULL,
    netmask CHAR(15) NOT NULL,
    gateway CHAR(15) NOT NULL,
    dns1 CHAR(15) NOT NULL DEFAULT '223.5.5.5',
    dns2 CHAR(15) NOT NULL DEFAULT '8.8.8.8',
    iops_base BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_pre_unit BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_cap BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_max BIGINT UNSIGNED NOT NULL DEFAULT 0,
    iops_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_base BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_pre_unit BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_cap BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_max BIGINT UNSIGNED NOT NULL DEFAULT 0,
    bps_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS log(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    type TINYINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    host CHAR(15),
    message VARCHAR(255) NOT NULL DEFAULT '',
    full_message TEXT,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE log ADD INDEX (host);


CREATE TABLE IF NOT EXISTS guest_cpu_memory(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guest_uuid CHAR(36) NOT NULL,
    cpu_load INT UNSIGNED NOT NULL,
    memory_available BIGINT UNSIGNED NOT NULL,
    memory_rate TINYINT UNSIGNED NOT NULL DEFAULT 0,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE guest_cpu_memory ADD INDEX (guest_uuid);
ALTER TABLE guest_cpu_memory ADD INDEX (cpu_load);
ALTER TABLE guest_cpu_memory ADD INDEX (memory_available);
ALTER TABLE guest_cpu_memory ADD INDEX (memory_rate);
ALTER TABLE guest_cpu_memory ADD INDEX (timestamp);
ALTER TABLE guest_cpu_memory ADD INDEX (guest_uuid, timestamp);


CREATE TABLE IF NOT EXISTS guest_traffic(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guest_uuid CHAR(36) NOT NULL,
    name VARCHAR(36) NOT NULL,
    rx_bytes BIGINT UNSIGNED NOT NULL,
    rx_packets BIGINT UNSIGNED NOT NULL,
    rx_errs BIGINT UNSIGNED NOT NULL,
    rx_drop BIGINT UNSIGNED NOT NULL,
    tx_bytes BIGINT UNSIGNED NOT NULL,
    tx_packets BIGINT UNSIGNED NOT NULL,
    tx_errs BIGINT UNSIGNED NOT NULL,
    tx_drop BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE guest_traffic ADD INDEX (guest_uuid);
ALTER TABLE guest_traffic ADD INDEX (rx_bytes);
ALTER TABLE guest_traffic ADD INDEX (rx_packets);
ALTER TABLE guest_traffic ADD INDEX (tx_bytes);
ALTER TABLE guest_traffic ADD INDEX (tx_packets);
ALTER TABLE guest_traffic ADD INDEX (timestamp);
ALTER TABLE guest_traffic ADD INDEX (guest_uuid, timestamp);


CREATE TABLE IF NOT EXISTS guest_disk_io(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    disk_uuid CHAR(36) NOT NULL,
    rd_req BIGINT UNSIGNED NOT NULL,
    rd_bytes BIGINT UNSIGNED NOT NULL,
    wr_req BIGINT UNSIGNED NOT NULL,
    wr_bytes BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE guest_disk_io ADD INDEX (disk_uuid);
ALTER TABLE guest_disk_io ADD INDEX (rd_req);
ALTER TABLE guest_disk_io ADD INDEX (rd_bytes);
ALTER TABLE guest_disk_io ADD INDEX (wr_req);
ALTER TABLE guest_disk_io ADD INDEX (wr_bytes);
ALTER TABLE guest_disk_io ADD INDEX (timestamp);
ALTER TABLE guest_disk_io ADD INDEX (disk_uuid, timestamp);


CREATE TABLE IF NOT EXISTS host_cpu_memory(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    node_id BIGINT UNSIGNED NOT NULL,
    cpu_load INT UNSIGNED NOT NULL,
    memory_available BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE host_cpu_memory ADD INDEX (node_id);
ALTER TABLE host_cpu_memory ADD INDEX (timestamp);
ALTER TABLE host_cpu_memory ADD INDEX (node_id, timestamp);


CREATE TABLE IF NOT EXISTS host_traffic(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    node_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(36) NOT NULL,
    rx_bytes BIGINT UNSIGNED NOT NULL,
    rx_packets BIGINT UNSIGNED NOT NULL,
    rx_errs BIGINT UNSIGNED NOT NULL,
    rx_drop BIGINT UNSIGNED NOT NULL,
    tx_bytes BIGINT UNSIGNED NOT NULL,
    tx_packets BIGINT UNSIGNED NOT NULL,
    tx_errs BIGINT UNSIGNED NOT NULL,
    tx_drop BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE host_traffic ADD INDEX (node_id);
ALTER TABLE host_traffic ADD INDEX (rx_bytes);
ALTER TABLE host_traffic ADD INDEX (rx_packets);
ALTER TABLE host_traffic ADD INDEX (tx_bytes);
ALTER TABLE host_traffic ADD INDEX (tx_packets);
ALTER TABLE host_traffic ADD INDEX (timestamp);
ALTER TABLE host_traffic ADD INDEX (node_id, timestamp);
ALTER TABLE host_traffic ADD INDEX (node_id, name, timestamp);


CREATE TABLE IF NOT EXISTS host_disk_usage_io(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    node_id BIGINT UNSIGNED NOT NULL,
    mountpoint VARCHAR(255) NOT NULL,
    used BIGINT UNSIGNED NOT NULL,
    rd_req BIGINT UNSIGNED NOT NULL,
    rd_bytes BIGINT UNSIGNED NOT NULL,
    wr_req BIGINT UNSIGNED NOT NULL,
    wr_bytes BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE host_disk_usage_io ADD INDEX (node_id);
ALTER TABLE host_disk_usage_io ADD INDEX (mountpoint);
ALTER TABLE host_disk_usage_io ADD INDEX (used);
ALTER TABLE host_disk_usage_io ADD INDEX (rd_req);
ALTER TABLE host_disk_usage_io ADD INDEX (rd_bytes);
ALTER TABLE host_disk_usage_io ADD INDEX (wr_req);
ALTER TABLE host_disk_usage_io ADD INDEX (wr_bytes);
ALTER TABLE host_disk_usage_io ADD INDEX (timestamp);
ALTER TABLE host_disk_usage_io ADD INDEX (node_id, mountpoint, timestamp);


CREATE TABLE IF NOT EXISTS ssh_key(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    label VARCHAR(255) NOT NULL,
    public_key TEXT,
    create_time BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE ssh_key ADD INDEX (label);


CREATE TABLE IF NOT EXISTS ssh_key_guest_mapping(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ssh_key_id BIGINT UNSIGNED NOT NULL,
    guest_uuid CHAR(36) NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE ssh_key_guest_mapping ADD UNIQUE INDEX (ssh_key_id, guest_uuid);
ALTER TABLE ssh_key_guest_mapping ADD INDEX (guest_uuid);


CREATE TABLE IF NOT EXISTS snapshot(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    label VARCHAR(255) NOT NULL,
    snapshot_id VARCHAR(255) NOT NULL,
    parent_id VARCHAR(255) NOT NULL,
    guest_uuid CHAR(36) NOT NULL,
    status TINYINT UNSIGNED NOT NULL DEFAULT 0,
    progress TINYINT UNSIGNED NOT NULL DEFAULT 0,
    create_time BIGINT UNSIGNED NOT NULL,
    xml TEXT NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE snapshot ADD INDEX (label);
ALTER TABLE snapshot ADD INDEX (snapshot_id);
ALTER TABLE snapshot ADD INDEX (guest_uuid);


CREATE TABLE IF NOT EXISTS snapshot_disk_mapping(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    snapshot_id VARCHAR(255) NOT NULL,
    disk_uuid CHAR(36) NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE snapshot_disk_mapping ADD UNIQUE INDEX (snapshot_id, disk_uuid);
ALTER TABLE snapshot_disk_mapping ADD INDEX (disk_uuid);


CREATE TABLE IF NOT EXISTS project(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(127) NOT NULL,
    description TEXT,
    create_time BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE project ADD INDEX (name);


CREATE TABLE IF NOT EXISTS service(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    project_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(127) NOT NULL,
    description TEXT,
    create_time BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE service ADD INDEX (project_id);
ALTER TABLE service ADD INDEX (name);


INSERT INTO project (name, description, create_time) VALUES ('我的项目', '由 JimV 创建的默认项目。', UNIX_TIMESTAMP(NOW()) * 1000000);
INSERT INTO service (project_id, name, description, create_time) VALUES (1, '服务组', '由 JimV 创建的默认服务组。', UNIX_TIMESTAMP(NOW()) * 1000000);


INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('CentOS-Systemd', '用作 Redhat Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('CentOS-SysV', '用作 Redhat SysV 系列的系统初始化。初始化操作依据 CentOS 6.8 来实现。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('Gentoo-OpenRC', '用作 Gentoo OpenRC 系列的系统初始化。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('CoreOS', '用作 CoreOS 系列的系统初始化。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('Windows', '用作 MS-Windows 系列的系统初始化。初始化操作依据 Windows 2012 来实现。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('WindowsMode2', '用作 MS-Windows 系列的系统初始化。初始化操作依据 WindowsXP 来实现。', 1);

-- For CentOS-Systemd
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (1, 1, 0, '/etc/resolv.conf', 'nameserver {DNS1}
nameserver {DNS2}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (1, 1, 1, '/etc/sysconfig/network-scripts/ifcfg-eth0', 'DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
BOOTPROTO="static"
IPADDR={IP}
NETMASK={NETMASK}
GATEWAY={GATEWAY}
DNS1={DNS1}
DNS2={DNS2}
IPV6INIT=no
NAME=eth0', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (1, 1, 2, '/etc/hostname', '{HOSTNAME}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (1, 0, 3, '', '', 'echo "root:{PASSWORD}" | chpasswd');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (1, 0, 4, '', '', 'mkdir -p /root/.ssh');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (1, 1, 5, '/root/.ssh/authorized_keys', '{SSH-KEY}', '');

-- For CentOS-SysV
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (2, 1, 0, '/etc/resolv.conf', 'nameserver {DNS1}
nameserver {DNS2}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (2, 1, 1, '/etc/sysconfig/network-scripts/ifcfg-eth0', 'DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
BOOTPROTO="static"
IPADDR={IP}
NETMASK={NETMASK}
GATEWAY={GATEWAY}
IPV6INIT=no
NAME=eth0', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (2, 1, 2, '/etc/sysconfig/network', 'NETWORKING=yes
HOSTNAME="{HOSTNAME}"', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (2, 0, 3, '', '', 'echo "root:{PASSWORD}" | chpasswd');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (2, 0, 4, '', '', 'mkdir -p /root/.ssh');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (2, 1, 5, '/root/.ssh/authorized_keys', '{SSH-KEY}', '');

-- For Gentoo-OpenRC
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 0, '/etc/resolv.conf', 'nameserver {DNS1}
nameserver {DNS2}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 1, '/etc/conf.d/net', 'config_eth0="{IP}/{NETMASK}"
routes_eth0="default via {GATEWAY}"', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 2, '/etc/conf.d/hostname', 'hostname="{HOSTNAME}"', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 0, 3, '', '', 'echo "root:{PASSWORD}" | chpasswd');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 0, 4, '', '', 'mkdir -p /root/.ssh');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 5, '/root/.ssh/authorized_keys', '{SSH-KEY}', '');

-- For CoreOS
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (4, 1, 0, '/etc/resolv.conf', 'nameserver {DNS1}
nameserver {DNS2}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (4, 1, 1, '/etc/systemd/network/00-eth0.network', '[Match]
Name=eth0

[Network]
DNS={DNS1}
Address={IP}/{NETMASK}
Gateway={GATEWAY}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (4, 1, 2, '/etc/hostname', '{HOSTNAME}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (4, 1, 5, '/home/core/.ssh/authorized_keys', '{SSH-KEY}', '');

-- For Windows
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (5, 1, 0, '/Windows/jimv_init.bat', 'netsh interface ip set address name="Ethernet" source=static {IP} {NETMASK} {GATEWAY}
netsh interface ip set dns "Ethernet" static {DNS1} primary
netsh interface ip add dns "Ethernet" {DNS2}
wmic computersystem where name="%COMPUTERNAME%" call rename name="{HOSTNAME}"
net user Administrator {PASSWORD}
timeout 3 > NUL
sc delete JimVInit
del C:\\Windows\\jimv_init.bat
timeout 2 > NUL
shutdown -r -t 0', '');

-- For WindowsXP
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (6, 1, 0, '/WINDOWS/jimv_init.bat', 'netsh interface ip set address name="Ethernet" source=static {IP} {NETMASK} {GATEWAY} 1
netsh interface ip set dns "Ethernet" static {DNS1} primary
netsh interface ip add dns "Ethernet" {DNS2}
wmic computersystem where name="%COMPUTERNAME%" call rename name="{HOSTNAME}"
net user Administrator {PASSWORD}
@ping 127.0.0.1 -n 3 > NUL
sc delete JimVInit
del C:\\WINDOWS\\jimv_init.bat
shutdown -r -t 0
@ping 127.0.0.1 -n 2 > NUL', '');


INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('CentOS-7.4', 'CentOS 7.4。', 'linux', 'centos', 7, 4, 'x86_64', 'CentOS Linux release 7.4.1708 (Core)', 1, 'icon-os icon-os-centos', 1);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('CentOS-6.8', 'CentOS 6.8。', 'linux', 'centos', 6, 8, 'x86_64', 'CentOS release 6.8 (Final)', 1, 'icon-os icon-os-centos', 2);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Gentoo-2.2', 'Gentoo 2.2。', 'linux', 'gentoo', 2, 2, 'x86_64', 'Gentoo Base System release 2.2', 1, 'icon-os icon-os-gentoo', 3);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('CoreOS-1855.4.0', 'CoreOS 1855.4.0。', 'linux', 'coreos', 1855, 4, 'x86_64', 'CoreOS Linux release 1855.4.0', 1, 'icon-os icon-os-coreos', 4);
-- https://docs.microsoft.com/en-us/windows/desktop/sysinfo/operating-system-version
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2016-Standard', 'Windows 2016 Standard。', 'windows', 'windows', 10, 0, 'x86_64', 'Windows Server 2016 Standard', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2012-R2-Standard', 'Windows 2012 R2 Standard。', 'windows', 'windows', 6, 3, 'x86_64', 'Windows Server 2012 R2 Standard', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2008-R2-Enterprise', 'Windows 2008 R2 Enterprise。', 'windows', 'windows', 6, 1, 'x86_64', 'Windows Server 2008 R2 Enterprise', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows7-Ultimate-SP1', 'Windows7 Ultimate SP1 x64。', 'windows', 'windows', 6, 1, 'x86_64', 'Windows7 Ultimate SP1 x64', 1, 'icon-os icon-os-windows', 5);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2003-R2-Enterprise-SP2', 'Windows 2003 R2 Enterprise SP2 x64。', 'windows', 'windows', 5, 2, 'x86_64', 'Windows 2003 R2 Enterprise SP2', 1, 'icon-os icon-os-windows', 6);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('WindowsXP-SP3', 'WindowsXP SP1 x64。', 'windows', 'windows', 5, 1, 'x86', 'Windows XP SP3', 1, 'icon-os icon-os-windows', 6);
