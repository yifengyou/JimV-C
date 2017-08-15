# DROP DATABASE IF EXISTS jimv;
CREATE DATABASE IF NOT EXISTS jimv CHARACTER SET utf8;
USE jimv;


CREATE TABLE IF NOT EXISTS guest(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL,
    label VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    remark VARCHAR(255) NOT NULL DEFAULT '',
    os_template_id BIGINT UNSIGNED NOT NULL,
    create_time BIGINT UNSIGNED NOT NULL,
    -- 运行时的状态用 status;
    status TINYINT UNSIGNED NOT NULL DEFAULT 0,
    on_host VARCHAR(128) NOT NULL DEFAULT '',
    cpu TINYINT UNSIGNED NOT NULL,
    memory INT UNSIGNED NOT NULL,
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
ALTER TABLE guest ADD INDEX (on_host);
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
    remark VARCHAR(255) NOT NULL DEFAULT '',
    sequence TINYINT NOT NULL,
    format CHAR(16) NOT NULL DEFAULT 'qcow2',
    -- 实例固有的状态用 state;
    state TINYINT UNSIGNED NOT NULL DEFAULT 0,
    create_time BIGINT UNSIGNED NOT NULL,
    guest_uuid CHAR(36) NOT NULL,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;

ALTER TABLE disk ADD INDEX (size);
ALTER TABLE disk ADD INDEX (guest_uuid);
ALTER TABLE disk ADD INDEX (remark);


CREATE TABLE IF NOT EXISTS os_template(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    label VARCHAR(255) NOT NULL,
    path VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    icon VARCHAR(255) NOT NULL,
    boot_job_id BIGINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS boot_job(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    use_for TINYINT UNSIGNED NOT NULL DEFAULT 0,
    remark VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS operate_rule(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    boot_job_id BIGINT UNSIGNED NOT NULL,
    kind TINYINT UNSIGNED NOT NULL DEFAULT 0,
    sequence TINYINT UNSIGNED NOT NULL DEFAULT 0,
    path VARCHAR(255) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    command TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS config(
    id BIGINT UNSIGNED NOT NULL DEFAULT 1,
    glusterfs_volume VARCHAR(255) NOT NULL,
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
    rsa_private text NOT NULL DEFAULT '',
    rsa_public text NOT NULL DEFAULT '',
    PRIMARY KEY (id))
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS log(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    type TINYINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    host CHAR(15),
    message VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE log ADD INDEX (host);


CREATE TABLE IF NOT EXISTS cpu_memory(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guest_uuid CHAR(36) NOT NULL,
    cpu_load INT UNSIGNED NOT NULL,
    memory_available BIGINT UNSIGNED NOT NULL,
    memory_unused BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE cpu_memory ADD INDEX (guest_uuid);
ALTER TABLE cpu_memory ADD INDEX (cpu_load);
ALTER TABLE cpu_memory ADD INDEX (timestamp);
ALTER TABLE cpu_memory ADD INDEX (guest_uuid, timestamp);


CREATE TABLE IF NOT EXISTS traffic(
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

ALTER TABLE traffic ADD INDEX (guest_uuid);
ALTER TABLE traffic ADD INDEX (rx_bytes);
ALTER TABLE traffic ADD INDEX (rx_packets);
ALTER TABLE traffic ADD INDEX (tx_bytes);
ALTER TABLE traffic ADD INDEX (tx_packets);
ALTER TABLE traffic ADD INDEX (timestamp);
ALTER TABLE traffic ADD INDEX (guest_uuid, timestamp);


CREATE TABLE IF NOT EXISTS disk_io(
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

ALTER TABLE disk_io ADD INDEX (disk_uuid);
ALTER TABLE disk_io ADD INDEX (rd_req);
ALTER TABLE disk_io ADD INDEX (rd_bytes);
ALTER TABLE disk_io ADD INDEX (wr_req);
ALTER TABLE disk_io ADD INDEX (wr_bytes);
ALTER TABLE disk_io ADD INDEX (timestamp);
ALTER TABLE disk_io ADD INDEX (disk_uuid, timestamp);


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


