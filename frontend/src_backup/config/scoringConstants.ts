/**
 * 评分系统常量定义
 * 功能：统一管理评分规则相关的常量、映射、枚举
 * 更新：2026-05-11
 */

// 角色类型定义
export const ROLE_TYPES = {
  DPS: 'dps',
  SUPPORT: 'support',
  TANK: 'tank',
  CONDITION: 'condition',
  HEALING: 'healing',
  CONTROL: 'control',
  UTILITY: 'utility',
} as const

export type RoleType = typeof ROLE_TYPES[keyof typeof ROLE_TYPES]

// 角色图标映射
export const ROLE_ICON_MAP: Record<RoleType, string> = {
  [ROLE_TYPES.DPS]: 'pi pi-bolt',
  [ROLE_TYPES.SUPPORT]: 'pi pi-heart',
  [ROLE_TYPES.TANK]: 'pi pi-shield',
  [ROLE_TYPES.CONDITION]: 'pi pi-fire',
  [ROLE_TYPES.HEALING]: 'pi pi-heart-fill',
  [ROLE_TYPES.CONTROL]: 'pi pi-lock',
  [ROLE_TYPES.UTILITY]: 'pi pi-wrench',
}

// 预定义渐变色映射
export const ROLE_GRADIENT_MAP: Record<RoleType, string> = {
  [ROLE_TYPES.DPS]: '#FF8A65',
  [ROLE_TYPES.SUPPORT]: '#00B4FF',
  [ROLE_TYPES.TANK]: '#165DFF',
  [ROLE_TYPES.CONDITION]: '#FF6B35',
  [ROLE_TYPES.HEALING]: '#00E5A0',
  [ROLE_TYPES.CONTROL]: '#6366F1',
  [ROLE_TYPES.UTILITY]: '#0EA5E9',
}

// 评分维度定义
export const DIMENSION_TYPES = {
  DAMAGE: 'damage',
  HEALING: 'healing',
  PROTECTION: 'protection',
  CROWD_CONTROL: 'crowd_control',
  SUPPORT: 'support',
  SURVIVAL: 'survival',
  OBJECTIVE: 'objective',
  DOWNSTACKS: 'downstacks',
} as const

export type DimensionType = typeof DIMENSION_TYPES[keyof typeof DIMENSION_TYPES]

// 维度图标映射
export const DIMENSION_ICONS: Record<DimensionType, string> = {
  [DIMENSION_TYPES.DAMAGE]: 'pi pi-bolt',
  [DIMENSION_TYPES.HEALING]: 'pi pi-heart',
  [DIMENSION_TYPES.PROTECTION]: 'pi pi-shield',
  [DIMENSION_TYPES.CROWD_CONTROL]: 'pi pi-lock',
  [DIMENSION_TYPES.SUPPORT]: 'pi pi-star',
  [DIMENSION_TYPES.SURVIVAL]: 'pi pi-users',
  [DIMENSION_TYPES.OBJECTIVE]: 'pi pi-flag',
  [DIMENSION_TYPES.DOWNSTACKS]: 'pi pi-arrow-down',
}

// 维度颜色映射
export const DIMENSION_COLORS: Record<DimensionType, string> = {
  [DIMENSION_TYPES.DAMAGE]: '#FF4D6A',
  [DIMENSION_TYPES.HEALING]: '#00D68F',
  [DIMENSION_TYPES.PROTECTION]: '#165DFF',
  [DIMENSION_TYPES.CROWD_CONTROL]: '#9D4EDD',
  [DIMENSION_TYPES.SUPPORT]: '#FFAA00',
  [DIMENSION_TYPES.SURVIVAL]: '#00B4FF',
  [DIMENSION_TYPES.OBJECTIVE]: '#4CAF50',
  [DIMENSION_TYPES.DOWNSTACKS]: '#FF5722',
}

// 评分等级定义
export const GRADE_LIST = [
  { grade: 'S', range: '≥90分', desc: '表现卓越，远超平均水平', color: '#FFD700', color2: '#FFA500' },
  { grade: 'A', range: '≥80分', desc: '表现优秀，高于平均水平', color: '#00D68F', color2: '#00B4FF' },
  { grade: 'B', range: '≥70分', desc: '表现良好，达到平均水平', color: '#165DFF', color2: '#4080FF' },
  { grade: 'C', range: '≥60分', desc: '表现一般，略低于平均', color: '#FFAA00', color2: '#FFB347' },
  { grade: 'D', range: '≥40分', desc: '表现较差，需要改进', color: '#FF6B35', color2: '#FF8A65' },
  { grade: 'F', range: '<40分', desc: '表现很差，急需提升', color: '#FF4D6A', color2: '#FF8A80' },
] as const

// 默认权重（百分比重）
export const DEFAULT_WEIGHT = 10
export const WEIGHT_MULTIPLIER = 0.01

// 评分模式
export const SCORING_MODES = {
  ROLE_BASED: 'role_based',
  PROFESSION_BASED: 'profession_based',
} as const

export type ScoringMode = typeof SCORING_MODES[keyof typeof SCORING_MODES]

// 规则范围
export const RULE_SCOPES = {
  GENERIC: 'generic',
  PROFESSION: 'profession',
} as const

export type RuleScope = typeof RULE_SCOPES[keyof typeof RULE_SCOPES]
