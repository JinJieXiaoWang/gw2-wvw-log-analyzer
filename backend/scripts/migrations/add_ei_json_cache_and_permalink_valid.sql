-- 迁移：新增 EI JSON 缓存和 permalink 验证字段
-- 适用：MySQL / SQLite
-- 日期：2026-05-13

-- evtc_log 表新增字段
ALTER TABLE evtc_log ADD COLUMN ei_json_cache TEXT NULL COMMENT 'gzip+base64压缩后的EI JSON缓存';
ALTER TABLE evtc_log ADD COLUMN ei_json_cached_at DATETIME NULL COMMENT 'EI JSON缓存时间';
ALTER TABLE evtc_log ADD COLUMN dps_report_permalink_valid INTEGER DEFAULT 1 COMMENT 'permalink是否有效: 1-有效, 0-失效';

-- 对于 SQLite，COMMENT 不支持，可简化为：
-- ALTER TABLE evtc_log ADD COLUMN ei_json_cache TEXT;
-- ALTER TABLE evtc_log ADD COLUMN ei_json_cached_at DATETIME;
-- ALTER TABLE evtc_log ADD COLUMN dps_report_permalink_valid INTEGER DEFAULT 1;
