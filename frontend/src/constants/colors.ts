/**
 * 颜色常量
 * 包含在多个组件中重复使用的十六进制色值与渐变色定义
 * 用于减少硬编码颜色，便于后续主题统一管理
 */

// ==================== 绿色系 - 治疗/生存/净化 ====================
export const COLOR_HEALING_START = '#22c55e'
export const COLOR_HEALING_END = '#16a34a'
export const COLOR_SURVIVAL_END = '#10b981'
export const COLOR_CLEANSE_START = '#22c55e'
export const COLOR_CLEANSE_END = '#10b981'

// ==================== 蓝色系 - 屏障/DPS ====================
export const COLOR_BARRIER_START = '#3b82f6'
export const COLOR_BARRIER_END = '#1d4ed8'
export const COLOR_DPS_START = '#3b82f6'
export const COLOR_DPS_END = '#8b5cf6'

// ==================== 紫色系 - HPS ====================
export const COLOR_HPS_START = '#8b5cf6'
export const COLOR_HPS_END = '#6d28d9'

// ==================== 橙黄色系 - 评分/过量治疗/指挥官 ====================
export const COLOR_SCORE_START = '#f59e0b'
export const COLOR_SCORE_END = '#eab308'
export const COLOR_SCORE_ALT_END = '#fbbf24'
export const COLOR_OVERHEAL_START = '#f59e0b'
export const COLOR_OVERHEAL_END = '#d97706'
export const COLOR_COMMANDER = '#f59e0b'

// ==================== 红色系 - 伤害 ====================
export const COLOR_DAMAGE_START = '#ef4444'
export const COLOR_DAMAGE_END = '#f97316'

// ==================== 排行奖牌色 ====================
export const COLOR_BRONZE_START = '#cd7f32'
export const COLOR_BRONZE_END = '#d4956a'
export const COLOR_SILVER_START = '#9ca3af'
export const COLOR_SILVER_END = '#d1d5db'

// ==================== 青色 - Buff/增益 ====================
export const COLOR_BOON_CYAN = '#06b6d4'

// ==================== 增益色值数组 ====================
export const BOON_COLORS = [
  COLOR_HEALING_START,
  COLOR_DPS_START,
  COLOR_SCORE_START,
  COLOR_DAMAGE_START,
  COLOR_DPS_END,
  COLOR_BOON_CYAN,
] as const
