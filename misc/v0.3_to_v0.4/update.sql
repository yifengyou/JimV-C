

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

ALTER TABLE os_template_image ADD COLUMN kind TINYINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE os_template_image ADD COLUMN progress TINYINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE os_template_image ADD COLUMN create_time BIGINT UNSIGNED NOT NULL;

