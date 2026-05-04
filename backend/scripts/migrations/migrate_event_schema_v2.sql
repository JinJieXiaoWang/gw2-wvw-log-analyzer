-- ============================================================
-- evtc_event 表精简迁移脚本
-- 目标：删除未使用字段和索引，降低存储开销
-- 注意：此操作会重建表，建议在低峰期执行
-- ============================================================

USE `gw2`;

-- ------------------------------------------------------------
-- 1. 删除无用索引（先删索引，快且不影响数据）
-- ------------------------------------------------------------
DROP INDEX IF EXISTS `uk_log_event_index` ON `evtc_event`;
DROP INDEX IF EXISTS `idx_dst_agent` ON `evtc_event`;
DROP INDEX IF EXISTS `idx_result` ON `evtc_event`;
DROP INDEX IF EXISTS `idx_skill` ON `evtc_event`;
DROP INDEX IF EXISTS `idx_time` ON `evtc_event`;
DROP INDEX IF EXISTS `idx_iff` ON `evtc_event`;
DROP INDEX IF EXISTS `idx_category_time` ON `evtc_event`;

-- ------------------------------------------------------------
-- 2. 删除未使用字段（MySQL 8.0 支持 INSTANT DDL 但仅适用于表尾字段；
--    这些字段分散在各处，MySQL 会自动选择 COPY 或 INPLACE 算法重建表）
-- ------------------------------------------------------------
ALTER TABLE `evtc_event` DROP COLUMN `event_index`;
ALTER TABLE `evtc_event` DROP COLUMN `time_sec`;
ALTER TABLE `evtc_event` DROP COLUMN `overstack_value`;
ALTER TABLE `evtc_event` DROP COLUMN `src_instid`;
ALTER TABLE `evtc_event` DROP COLUMN `dst_instid`;
ALTER TABLE `evtc_event` DROP COLUMN `src_master_instid`;
ALTER TABLE `evtc_event` DROP COLUMN `dst_master_instid`;
ALTER TABLE `evtc_event` DROP COLUMN `is_ninety`;
ALTER TABLE `evtc_event` DROP COLUMN `is_fifty`;
ALTER TABLE `evtc_event` DROP COLUMN `is_moving`;
ALTER TABLE `evtc_event` DROP COLUMN `is_shields`;
ALTER TABLE `evtc_event` DROP COLUMN `is_offcycle`;
ALTER TABLE `evtc_event` DROP COLUMN `event_category`;

-- ------------------------------------------------------------
-- 3. 验证结果
-- ------------------------------------------------------------
SELECT 
    TABLE_NAME,
    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS total_mb,
    TABLE_ROWS
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'evtc_event' AND TABLE_SCHEMA = DATABASE();
