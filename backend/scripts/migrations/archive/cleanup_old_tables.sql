-- ============================================================================
-- 数据库清理脚本
-- 作者：系统
-- 创建日期：2026-05-02
-- 说明：删除旧表结构，保留符合新规范的表
-- ============================================================================
-- 保留的表前缀：
--   - evtc_ (EVTC原始数据)
--   - sys_ (系统字典)
--   - storage_ (存储管理)
--   - ei_ (EI解析数据)
--   - ai_ (AI分析数据)
--   - batch_parse (批量解析)
-- ============================================================================

-- 先禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 删除需要清理的表（按依赖关系从子表到父表）
-- ============================================================================

-- Build相关表
DROP TABLE IF EXISTS `builds`;

-- Member相关表
DROP TABLE IF EXISTS `members`;

-- Profession Role相关表
DROP TABLE IF EXISTS `profession_role_condition_expression`;
DROP TABLE IF EXISTS `profession_role_rules`;
DROP TABLE IF EXISTS `role_templates`;
DROP TABLE IF EXISTS `profession_roles`;

-- Skill相关表
DROP TABLE IF EXISTS `skill_events`;
DROP TABLE IF EXISTS `skills`;

-- Fight相关表
DROP TABLE IF EXISTS `fight_details`;
DROP TABLE IF EXISTS `fight_stats`;
DROP TABLE IF EXISTS `fights`;

-- 旧的管理员表（已迁移到sys_user）
DROP TABLE IF EXISTS `admins`;

-- ============================================================================
-- 更新 evtc_log 表的外键引用（从admins改为sys_user）
-- ============================================================================
ALTER TABLE IF EXISTS `evtc_log` 
DROP FOREIGN KEY IF EXISTS `fk_log_uploader`,
DROP INDEX IF EXISTS `idx_log_uploader_id`;

ALTER TABLE IF EXISTS `evtc_log` 
CHANGE COLUMN IF EXISTS `uploaded_by` `uploaded_by` INT NULL AFTER `upload_ip`,
ADD CONSTRAINT `fk_log_uploader` 
    FOREIGN KEY (`uploaded_by`) 
    REFERENCES `sys_user`(`id`) 
    ON DELETE SET NULL,
ADD INDEX `idx_log_uploader_id` (`uploaded_by`);

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 验证清理结果
-- ============================================================================
SELECT 
    TABLE_NAME,
    TABLE_COMMENT
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME NOT REGEXP '^(evtc_|sys_|storage_|ei_|ai_|batch_parse)'
ORDER BY TABLE_NAME;

SELECT '清理完成！保留的表已列出，其余表已删除。' AS Result;
