/**
 * Build Library 类型定义
 * 基于 Yuque 知识库《激战2《格林特职业学院》战场配置》的4段式文档结构
 *
 * 数据验证规则（前端/后端通用）：
 * - id: 必填，系统生成，前端创建时留空
 * - title: 必填，2-100字符
 * - profession: 必填，必须在有效职业列表中
 * - role: 必填，'dps' | 'support'
 * - bdCode: 必填，必须符合 GW2 Build Code 格式 [&...=]
 * - author: 必填，1-50字符
 * - updatedAt: ISO 8601 格式，前端自动填充
 * - wordCount: 只读，后端计算或前端统计
 * - isMeta: 只读，由后端标记或管理员设置
 */

export interface BuildWeapon {
  set: number
  name: string
  sigils: string[]
}

export interface BuildTraitLine {
  name: string
  choices: [number, number, number]
}

export interface BuildRotationCommand {
  callout: string
  action: string
  note?: string
}

export interface BuildMechanic {
  name: string
  sources: string[]
}

export interface BuildVideo {
  title: string
  url: string
  author?: string
}

export interface BuildEntry {
  id: string
  slug: string
  title: string
  profession: string
  professionColor: string
  eliteSpec: string | null
  role: 'dps' | 'support'
  subRoles: ('boon' | 'heal' | 'tank' | 'cc')[]
  armorType: string
  weapons: BuildWeapon[]
  relic: string
  rune: string
  food: string
  wrench: string
  infusion: string
  attrRequirements: string[]
  bdCode: string
  traitLines: BuildTraitLine[]
  rotationCommands: BuildRotationCommand[]
  mechanics: BuildMechanic[]
  videos: BuildVideo[]
  author: string
  updatedAt: string
  wordCount: number
  isMeta: boolean
}

/** 创建 Build 时的请求 DTO（前端表单 → 后端/模拟服务） */
export interface BuildCreateDto {
  title: string
  profession: string
  eliteSpec: string | null
  role: 'dps' | 'support'
  subRoles: string[]
  armorType: string
  weapons: BuildWeapon[]
  relic: string
  rune: string
  food: string
  wrench: string
  infusion: string
  attrRequirements: string[]
  bdCode: string
  traitLines: BuildTraitLine[]
  rotationCommands: BuildRotationCommand[]
  mechanics: BuildMechanic[]
  videos: BuildVideo[]
  author: string
  isMeta?: boolean
}

/** 更新 Build 时的请求 DTO */
export type BuildUpdateDto = Partial<BuildCreateDto>

/** 字段级验证错误 */
export interface ValidationError {
  field: string
  message: string
  code: string
}

/** 表单验证结果 */
export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
}

/** 标准 API 响应格式（与后端接口对齐） */
export interface BuildApiResponse<T> {
  success: boolean
  code: number
  message: string
  data: T
  timestamp: string
}

/** Build 列表分页响应 */
export interface BuildListResponse {
  items: BuildEntry[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

/** 有效职业常量（与 professionUtils.ts 保持一致） */
export const VALID_PROFESSIONS = [
  'Elementalist', 'Engineer', 'Guardian', 'Mesmer',
  'Necromancer', 'Ranger', 'Revenant', 'Warrior'
] as const

export type ValidProfession = (typeof VALID_PROFESSIONS)[number]

/** 职业颜色映射（前端默认值，可被后端覆盖） */
export const PROFESSION_COLORS: Record<string, string> = {
  Warrior: '#E85D04',
  Guardian: '#FAA307',
  Revenant: '#9D4EDD',
  Ranger: '#06D6A0',
  Engineer: '#7B8FA1',
  Necromancer: '#8D0801',
  Mesmer: '#4361EE',
  Elementalist: '#FF6B6B'
}

export type ProfessionFilter = 'all' | string
export type RoleFilter = 'all' | 'dps' | 'support'
export type SubRoleFilter = 'all' | 'boon' | 'heal' | 'tank' | 'cc'

export interface BuildFilterState {
  profession: ProfessionFilter
  role: RoleFilter
  subRoles: SubRoleFilter[]
  searchQuery: string
  sortBy: 'updated' | 'profession' | 'name'
}
