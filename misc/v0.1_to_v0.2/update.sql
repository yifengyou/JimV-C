
ALTER TABLE config ADD COLUMN iops_base BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN iops_pre_unit BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN iops_cap BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN iops_max BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN iops_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN bps_base BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN bps_pre_unit BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN bps_cap BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN bps_max BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE config ADD COLUMN bps_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0;

ALTER TABLE disk ADD COLUMN iops BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN iops_rd BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN iops_wr BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN iops_max BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN iops_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN bps BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN bps_rd BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN bps_wr BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN bps_max BIGINT UNSIGNED NOT NULL DEFAULT 0;
ALTER TABLE disk ADD COLUMN bps_max_length BIGINT UNSIGNED NOT NULL DEFAULT 0;

-- 初始化 config 表中的磁盘限额参数；
UPDATE config SET iops_base=1000, iops_pre_unit=1, iops_cap=2000, iops_max=3000, iops_max_length=20,
    bps_base=1024 * 1024 * 200, bps_pre_unit=1024 * 1024 * 0.3, bps_cap=1024 * 1024 * 500, bps_max=1024 * 1024 * 1024,
    bps_max_length=10;

-- 更新虚拟机系统盘磁盘性能限额；
UPDATE disk, config SET
    disk.iops=config.iops_base, disk.iops_max=config.iops_max, disk.iops_max_length=config.iops_max_length,
    disk.bps=config.bps_base, disk.bps_max=config.bps_max, disk.bps_max_length=config.bps_max_length
WHERE disk.sequence=0 AND config.id=1;

-- 更新小于满额的非系统盘磁盘性能限额；
UPDATE disk, config SET
    disk.iops=config.iops_base + config.iops_pre_unit * disk.size,
    disk.iops_max=config.iops_max, disk.iops_max_length=config.iops_max_length,
    disk.bps=config.bps_base + config.bps_pre_unit * disk.size,
    disk.bps_max=config.bps_max, disk.bps_max_length=config.bps_max_length
WHERE disk.sequence!=0 AND disk.size<=1000 AND config.id=1;

-- 更新超出满额的非系统盘磁盘性能限额；
UPDATE disk, config SET
    disk.iops=config.iops_cap,
    disk.iops_max=config.iops_max, disk.iops_max_length=config.iops_max_length,
    disk.bps=config.bps_cap,
    disk.bps_max=config.bps_max, disk.bps_max_length=config.bps_max_length
WHERE disk.sequence!=0 AND disk.size>1000 AND config.id=1;


-- on_host 变更为 node_id
ALTER TABLE guest ADD COLUMN node_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE disk ADD COLUMN node_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE guest ADD INDEX (node_id);
ALTER TABLE disk ADD INDEX (node_id);

-- import jimit as ji
-- from models import Utils
-- on_host=ji.Common.get_hostname()
-- node_id=Utils.uuid_by_decimal(_str=ji.Common.get_hostname(), _len=16)
-- UPDATE guest SET node_id='' WHERE on_host='';
-- UPDATE disk SET node_id='' WHERE on_host='';

-- 删除 on_host 字段
-- ALTER TABLE guest DROP on_host;
-- ALTER TABLE disk DROP on_host;

-- 更新 旧 node_id 的值为新 node_id 值
-- import uuid
-- old_node_id=uuid.getnode()
-- new_node_id=Utils.uuid_by_decimal(_str=ji.Common.get_hostname(), _len=16)
-- UPDATE host_cpu_memory SET node_id=new_node_id WHERE node_id=old_node_id;
-- UPDATE host_traffic SET node_id=new_node_id WHERE node_id=old_node_id;
-- UPDATE host_disk_usage_io SET node_id=new_node_id WHERE node_id=old_node_id;
