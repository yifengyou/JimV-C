USE jimv;

CREATE TABLE IF NOT EXISTS ip_pool(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    start_ip CHAR(15) NOT NULL,
    end_ip CHAR(15) NOT NULL,
    netmask CHAR(15) NOT NULL,
    gateway CHAR(15) NOT NULL,
    dns1 CHAR(15) NOT NULL DEFAULT '223.5.5.5',
    dns2 CHAR(15) NOT NULL DEFAULT '8.8.8.8',
    activity TINYINT UNSIGNED NOT NULL DEFAULT 0,
    name VARCHAR(127) NOT NULL,
    description TEXT,
    create_time BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE ip_pool ADD INDEX (name);

INSERT INTO ip_pool (start_ip, end_ip, netmask, gateway, dns1, dns2, activity, name, description, create_time)
    SELECT start_ip, end_ip, netmask, gateway, dns1, dns2, 1, 'Default', '默认 IP 池。', UNIX_TIMESTAMP(NOW()) * 1000000
    FROM config;

ALTER TABLE config
    DROP COLUMN start_ip,
    DROP COLUMN end_ip,
    DROP COLUMN start_vnc_port,
    DROP COLUMN netmask,
    DROP COLUMN gateway,
    DROP COLUMN dns1,
    DROP COLUMN dns2;


CREATE TABLE IF NOT EXISTS reserved_ip(
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    ip CHAR(15) NOT NULL,
    create_time BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id))
    ENGINE=Innodb
    DEFAULT CHARSET=utf8;

ALTER TABLE reserved_ip ADD INDEX (ip);

ALTER TABLE guest ADD COLUMN autostart BOOLEAN NOT NULL DEFAULT FALSE ;
ALTER TABLE guest ADD INDEX (autostart);
