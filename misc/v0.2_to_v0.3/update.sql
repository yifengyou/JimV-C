

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


-- 操作系统模板镜像
CREATE TABLE IF NOT EXISTS os_template_image(
    label VARCHAR(255) NOT NULL,
    description TEXT,
    path VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    logo VARCHAR(255) NOT NULL,
    os_template_profile_id BIGINT UNSIGNED NOT NULL,
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



INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('CentOS-Systemd', '用作 Redhat Systemd 系列的系统初始化。初始化操作依据 CentOS 7 来实现。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('CentOS-SysV', '用作 Redhat SysV 系列的系统初始化。初始化操作依据 CentOS 6.8 来实现。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('Gentoo-OpenRC', '用作 Gentoo OpenRC 系列的系统初始化。', 1);
INSERT INTO os_template_initialize_operate_set (label, description, active) VALUES ('Windows', '用作 MS-Windows 系列的系统初始化。初始化操作依据 Windows 2012 来实现。', 1);

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

-- For Gentoo-OpenRC
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 0, '/etc/resolv.conf', 'nameserver {DNS1}
nameserver {DNS2}', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 1, '/etc/conf.d/net', 'config_eth0="{IP}/{NETMASK}"
routes_eth0="default via {GATEWAY}"', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 1, 2, '/etc/conf.d/hostname', 'hostname="{HOSTNAME}"', '');
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (3, 0, 3, '', '', 'echo "root:{PASSWORD}" | chpasswd');

-- For Windows
INSERT INTO os_template_initialize_operate (os_template_initialize_operate_set_id, kind, sequence, path, content, command) VALUES (4, 1, 0, '/Windows/jimv_init.bat', 'netsh interface ip set address name="Ethernet" source=static {IP} {NETMASK} {GATEWAY}
netsh interface ip set dns "Ethernet" static {DNS1} primary
netsh interface ip add dns "Ethernet" {DNS2}
wmic computersystem where name="%COMPUTERNAME%" call rename name="{HOSTNAME}"
net user Administrator {PASSWORD}
timeout 3 > NUL
sc delete JimVInit
del C:\\Windows\\jimv_init.bat
timeout 2 > NUL
shutdown -r -t 0', '');


INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('CentOS-7.4', 'CentOS 7.4。', 'linux', 'centos', 7, 4, 'x86_64', 'CentOS Linux release 7.4.1708 (Core)', 1, 'icon-os icon-os-centos', 1);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('CentOS-6.8', 'CentOS 6.8。', 'linux', 'centos', 6, 8, 'x86_64', 'CentOS release 6.8 (Final)', 1, 'icon-os icon-os-centos', 2);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Gentoo-2.2', 'Gentoo 2.2。', 'linux', 'gentoo', 2, 2, 'x86_64', 'Gentoo Base System release 2.2', 1, 'icon-os icon-os-gentoo', 3);
INSERT INTO os_template_profile (label, description, os_type, os_distro, os_major, os_minor, os_arch, os_product_name, active, icon, os_template_initialize_operate_set_id)
VALUES ('Windows-2012-R2-Standard', 'Windows 2012 R2 Standard。', 'windows', 'windows', 6, 3, 'x86_64', 'Windows Server 2012 R2 Standard', 1, 'icon-os icon-os-windows', 4);

