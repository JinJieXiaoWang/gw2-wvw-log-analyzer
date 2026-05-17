-- ============================================
-- Buff 数据一致性修复脚本
-- 修复 gw_buff 表中的错误 ID→名称映射
-- 基于 EI JSON 实际数据验证（dps.report API）
-- ============================================

-- 1. 更新 gw_buff 表：修正错误的 buff 名称和中文名
UPDATE gw_buff SET name = 'Protection', name_cn = '保护', category = 'defensive', description = '减少受到的伤害' WHERE id = 717;
UPDATE gw_buff SET name = 'Regeneration', name_cn = '再生', category = 'healing', description = '持续恢复生命值' WHERE id = 718;
UPDATE gw_buff SET name = 'Swiftness', name_cn = '迅捷', category = 'utility', description = '增加移动速度' WHERE id = 719;
UPDATE gw_buff SET name = 'Vigor', name_cn = '活力', category = 'defensive', description = '增加耐力恢复速度' WHERE id = 726;
UPDATE gw_buff SET name = 'Resistance', name_cn = '抗性', category = 'defensive', description = '减少症状伤害' WHERE id = 26980;
UPDATE gw_buff SET name = 'Reinforced Armor', name_cn = '强化护甲', category = 'defensive', description = 'WvW 中 Vigor 的替代形式，增加耐力恢复速度' WHERE id = 9283;
UPDATE gw_buff SET name = 'Resolution', name_cn = '决心', category = 'defensive', description = '减少症状持续时间' WHERE id = 873;

-- 2. 删除错误的记录（11887 在 EI JSON 中不存在）
DELETE FROM gw_buff WHERE id = 11887;

-- 3. 添加缺失的记录
INSERT OR IGNORE INTO gw_buff (id, name, name_cn, category, stacking, max_stacks, is_key_buff, icon, description)
VALUES (1122, 'Stability', '稳固', 'defensive', 'intensity', 25, 1, 'Stability.png', '免疫控制效果');

INSERT OR IGNORE INTO gw_buff (id, name, name_cn, category, stacking, max_stacks, is_key_buff, icon, description)
VALUES (873, 'Resolution', '决心', 'defensive', 'duration', 1, 0, 'Resolution.png', '减少症状持续时间');

INSERT OR IGNORE INTO gw_buff (id, name, name_cn, category, stacking, max_stacks, is_key_buff, icon, description)
VALUES (719, 'Swiftness', '迅捷', 'utility', 'duration', 1, 0, 'Swiftness.png', '增加移动速度');

-- 4. 修正中文名不一致的记录
UPDATE gw_buff SET name_cn = '威能' WHERE id = 740;
UPDATE gw_buff SET name_cn = '激怒' WHERE id = 725;
UPDATE gw_buff SET name_cn = '敏捷' WHERE id = 1187;
UPDATE gw_buff SET name_cn = '急速' WHERE id = 30328;
UPDATE gw_buff SET name_cn = '保护' WHERE id = 717;
UPDATE gw_buff SET name_cn = '圣盾' WHERE id = 743;
UPDATE gw_buff SET name_cn = '稳固' WHERE id = 1122;
UPDATE gw_buff SET name_cn = '抗性' WHERE id = 26980;
UPDATE gw_buff SET name_cn = '活力' WHERE id = 726;
