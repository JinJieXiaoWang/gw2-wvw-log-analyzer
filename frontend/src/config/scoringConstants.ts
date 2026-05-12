/**
 * 评分系统常量定义
 * 功能：统一管理评分规则相关的常量、映射、枚举
 * 更新：2026-05-11
 */
import { Colors } from '@/config/designTokens'

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
  [ROLE_TYPES.DPS]: Colors.palette.salmon,
  [ROLE_TYPES.SUPPORT]: Colors.palette.skyBlue,
  [ROLE_TYPES.TANK]: Colors.primary.DEFAULT,
  [ROLE_TYPES.CONDITION]: Colors.palette.orangeRed,
  [ROLE_TYPES.HEALING]: Colors.palette.aqua,
  [ROLE_TYPES.CONTROL]: Colors.palette.indigo,
  [ROLE_TYPES.UTILITY]: Colors.palette.sky,
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
  [DIMENSION_TYPES.DAMAGE]: Colors.palette.roseBright,
  [DIMENSION_TYPES.HEALING]: Colors.palette.mint,
  [DIMENSION_TYPES.PROTECTION]: Colors.primary.DEFAULT,
  [DIMENSION_TYPES.CROWD_CONTROL]: Colors.palette.violetBright,
  [DIMENSION_TYPES.SUPPORT]: Colors.palette.orangeBright,
  [DIMENSION_TYPES.SURVIVAL]: Colors.palette.skyBlue,
  [DIMENSION_TYPES.OBJECTIVE]: Colors.palette.materialGreen,
  [DIMENSION_TYPES.DOWNSTACKS]: Colors.palette.deepOrange,
}

// 评分等级定义
export const GRADE_LIST = [
  { grade: 'S', range: '≥90分', desc: '表现卓越，远超平均水平', color: Colors.palette.gold, color2: Colors.palette.orangeGold },
  { grade: 'A', range: '≥80分', desc: '表现优秀，高于平均水平', color: Colors.palette.mint, color2: Colors.palette.skyBlue },
  { grade: 'B', range: '≥70分', desc: '表现良好，达到平均水平', color: Colors.primary.DEFAULT, color2: Colors.primary.light },
  { grade: 'C', range: '≥60分', desc: '表现一般，略低于平均', color: Colors.palette.orangeBright, color2: Colors.palette.peach },
  { grade: 'D', range: '≥40分', desc: '表现较差，需要改进', color: Colors.palette.orangeRed, color2: Colors.palette.salmon },
  { grade: 'F', range: '<40分', desc: '表现很差，急需提升', color: Colors.palette.roseBright, color2: Colors.palette.lightRed },
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
