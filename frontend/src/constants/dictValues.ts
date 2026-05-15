/**
 * 字典业务常量模块（前端）
 * 功能：与后端 constants/dict_values.py 对应，避免在代码中直接写死字典值字符串
 * 使用原则：
 *   1. 条件判断状态/类型时，优先使用本模块常量
 *   2. 新增字典类型时，如需要在代码中判断，应同步在本模块定义对应常量
 *   3. 常量值必须与后端 database/init_all.py 中的种子数据保持一致
 *
 * 作者：系统
 * 创建日期：2026-05-15
 */

// =============================================================================
// 解析状态 (parse_status)
// =============================================================================

export const ParseStatus = {
  PENDING: 'pending',
  PARSING: 'parsing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  RETRYING: 'retrying',
  PARTIAL: 'partial',
} as const

export type ParseStatusValue = (typeof ParseStatus)[keyof typeof ParseStatus]

/** 是否为终态 */
export function isTerminalParseStatus(status: string): boolean {
  return status === ParseStatus.COMPLETED || status === ParseStatus.FAILED || status === ParseStatus.PARTIAL
}

/** 是否处理中 */
export function isProcessingParseStatus(status: string): boolean {
  return status === ParseStatus.PARSING || status === ParseStatus.RETRYING
}

// =============================================================================
// 角色定位 (role)
// =============================================================================

export const RoleType = {
  DPS: 'dps',
  SUPPORT: 'support',
  TANK: 'tank',
  CONDITION: 'condition',
  HEALING: 'healing',
  CONTROL: 'control',
  UTILITY: 'utility',
} as const

export type RoleTypeValue = (typeof RoleType)[keyof typeof RoleType]

/** 获取默认角色类型 */
export function getDefaultRoleType(): string {
  return RoleType.DPS
}

/** 是否为输出向角色 */
export function isDamageRole(roleType: string): boolean {
  return roleType === RoleType.DPS || roleType === RoleType.CONDITION
}

/** 是否为辅助向角色 */
export function isSupportRole(roleType: string): boolean {
  return roleType === RoleType.SUPPORT || roleType === RoleType.HEALING || roleType === RoleType.TANK
}

// =============================================================================
// 通用状态 (sys_normal_disable)
// =============================================================================

export const NormalDisable = {
  ENABLED: 0,
  DISABLED: 1,
} as const

export type NormalDisableValue = (typeof NormalDisable)[keyof typeof NormalDisable]

export function isEnabled(status: number): boolean {
  return status === NormalDisable.ENABLED
}

export function isDisabled(status: number): boolean {
  return status === NormalDisable.DISABLED
}

// =============================================================================
// 是/否 (sys_yes_no)
// =============================================================================

export const YesNo = {
  YES: 'Y',
  NO: 'N',
} as const

export type YesNoValue = (typeof YesNo)[keyof typeof YesNo]

// =============================================================================
// 评分等级 (grade_level)
// =============================================================================

export const GradeLevel = {
  S: 's',
  A: 'a',
  B: 'b',
  C: 'c',
  D: 'd',
  F: 'f',
} as const

export type GradeLevelValue = (typeof GradeLevel)[keyof typeof GradeLevel]

// =============================================================================
// 评分规则版本状态 (scoring_rule_status)
// =============================================================================

export const ScoringRuleStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const

export type ScoringRuleStatusValue = (typeof ScoringRuleStatus)[keyof typeof ScoringRuleStatus]
