
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


ALTER TABLE guest ADD COLUMN service_id BIGINT UNSIGNED NOT NULL DEFAULT 1;
ALTER TABLE guest ADD INDEX (service_id);

