
ALTER TABLE guest_cpu_memory CHANGE COLUMN memory_unused memory_rate TINYINT UNSIGNED NOT NULL DEFAULT 0;

ALTER TABLE guest_cpu_memory ADD INDEX (memory_available);
ALTER TABLE guest_cpu_memory ADD INDEX (memory_rate);