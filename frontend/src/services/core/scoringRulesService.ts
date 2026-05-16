/**
 * 评分规则管理 API 服务（v3.0）
 * 支持通用规则 + 职业特定规则 + 版本管理 + 重算任务
 */

import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'

export interface ScoringRule {
  id: number
  role_type: string
  profession?: string | null
  dimension: string
  weight: number
  min_value?: number
  max_value?: number
  is_active: boolean
  description?: string
  sort_order: number
  created_at?: string
  updated_at?: string
}

export interface ScoringRuleGroup {
  role_type: string
  role_label: string
  profession?: string | null
  rules: ScoringRule[]
}

export interface DimensionInfo {
  key: string
  label: string
}

export interface ScoringRuleVersion {
  id: number
  version: number
  description?: string
  status: string
  total_records: number
  updated_records: number
  failed_records: number
  progress_percent?: number
  created_at?: string
  completed_at?: string
}

export interface RecalculateFilters {
  fight_ids?: number[]
  date_from?: string
  date_to?: string
  professions?: string[]
  account_names?: string[]
}

class ScoringRulesService {
  /** 获取角色类型列表 */
  async getRoleTypes(): Promise<Record<string, unknown>[]> {
    const resp = await apiFactory.get<Record<string, unknown>[]>(API_ENDPOINTS.SCORING_RULES.ROLES)
    return resp.success && resp.data ? resp.data : []
  }

  /** 获取评分规则（按角色类型和职业） */
  async getRules(roleType?: string, profession?: string | null): Promise<unknown> {
    const params: Record<string, unknown> = {}
    if (roleType) params.role_type = roleType
    if (profession) params.profession = profession
    const resp = await apiFactory.get<unknown>(API_ENDPOINTS.SCORING_RULES.RULES, { params })
    return resp.success && resp.data ? resp.data : null
  }

  /** 获取评分维度列表 */
  async getDimensions(): Promise<DimensionInfo[]> {
    const resp = await apiFactory.get<DimensionInfo[]>(API_ENDPOINTS.SCORING_RULES.DIMENSIONS)
    return resp.success && resp.data ? resp.data : []
  }

  /** 创建规则 */
  async createRule(data: Partial<ScoringRule>): Promise<ScoringRule | null> {
    const resp = await apiFactory.post<ScoringRule>(API_ENDPOINTS.SCORING_RULES.RULES, data)
    return resp.success && resp.data ? resp.data : null
  }

  /** 更新规则 */
  async updateRule(id: number, data: Partial<ScoringRule>): Promise<ScoringRule | null> {
    const resp = await apiFactory.put<ScoringRule>(API_ENDPOINTS.SCORING_RULES.RULE_UPDATE(id), data)
    return resp.success && resp.data ? resp.data : null
  }

  /** 删除规则 */
  async deleteRule(id: number): Promise<boolean> {
    const resp = await apiFactory.delete(API_ENDPOINTS.SCORING_RULES.RULE_DELETE(id))
    return resp.success
  }

  /** 批量更新（支持职业特定规则） */
  async batchUpdate(roleType: string, rules: Partial<ScoringRule>[], profession?: string | null, autoBumpVersion: boolean = true): Promise<unknown> {
    const resp = await apiFactory.post<unknown>(API_ENDPOINTS.SCORING_RULES.BATCH, {
      role_type: roleType,
      profession,
      rules,
    }, {
      params: autoBumpVersion ? { auto_bump_version: 'true' } : undefined
    })
    return resp.success && resp.data ? resp.data : null
  }

  /** 重置为默认 */
  async resetDefault(roleType?: string): Promise<unknown> {
    const params: Record<string, unknown> = {}
    if (roleType) params.role_type = roleType
    const resp = await apiFactory.post<unknown>(API_ENDPOINTS.SCORING_RULES.RESET, null, { params })
    return resp.success && resp.data ? resp.data : null
  }

  // ==================== 职业特定规则 ====================

  /** 获取已配置职业特定规则的职业列表 */
  async getProfessionsWithRules(): Promise<string[]> {
    const resp = await apiFactory.get<{ professions: string[]; count: number }>(API_ENDPOINTS.SCORING_RULES.PROFESSIONS)
    return resp.success && resp.data ? resp.data.professions || [] : []
  }

  /** 为指定职业创建/更新完整规则集 */
  async upsertProfessionRules(profession: string, roleType: string, rules: Partial<ScoringRule>[]): Promise<unknown> {
    const resp = await apiFactory.post<unknown>(API_ENDPOINTS.SCORING_RULES.PROFESSION_RULES(profession), {
      role_type: roleType,
      rules,
    })
    return resp.success && resp.data ? resp.data : null
  }

  /** 删除职业特定规则 */
  async deleteProfessionRules(profession: string, roleType?: string): Promise<unknown> {
    const params: Record<string, unknown> = {}
    if (roleType) params.role_type = roleType
    const resp = await apiFactory.delete<unknown>(API_ENDPOINTS.SCORING_RULES.PROFESSION_RULES(profession), { params })
    return resp.success && resp.data ? resp.data : null
  }

  // ==================== 版本管理 ====================

  /** 获取规则版本历史 */
  async getVersions(skip: number = 0, limit: number = 20): Promise<ScoringRuleVersion[]> {
    const resp = await apiFactory.get<ScoringRuleVersion[]>(API_ENDPOINTS.SCORING_RULES.VERSIONS, {
      params: { skip, limit }
    })
    return resp.success && resp.data ? resp.data : []
  }

  /** 获取版本详情 */
  async getVersionDetail(versionId: number): Promise<ScoringRuleVersion | null> {
    const resp = await apiFactory.get<ScoringRuleVersion>(API_ENDPOINTS.SCORING_RULES.VERSION_DETAIL(versionId))
    return resp.success && resp.data ? resp.data : null
  }

  /** 手动递增规则版本 */
  async bumpVersion(description?: string): Promise<ScoringRuleVersion | null> {
    const resp = await apiFactory.post<ScoringRuleVersion>(API_ENDPOINTS.SCORING_RULES.VERSION_BUMP, null, {
      params: description ? { description } : undefined
    })
    return resp.success && resp.data ? resp.data : null
  }

  // ==================== 重算任务 ====================

  /** 触发评分重算任务 */
  async triggerRecalculation(filters?: RecalculateFilters, description?: string): Promise<{ version_id: number; version: number; status: string } | null> {
    const resp = await apiFactory.post<any>(API_ENDPOINTS.SCORING.RECALCULATE, {
      filters: filters || {},
      description,
    })
    if (resp.success && resp.data && resp.data.version_id != null) {
      return {
        version_id: resp.data.version_id,
        version: resp.data.version,
        status: resp.data.status,
      }
    }
    return null
  }

  /** 获取重算任务进度 */
  async getRecalculationStatus(versionId: number): Promise<unknown> {
    const resp = await apiFactory.get<unknown>(API_ENDPOINTS.SCORING.RECALCULATE_STATUS(versionId))
    return resp.success && resp.data ? resp.data : null
  }
}

export const scoringRulesService = new ScoringRulesService()
export default scoringRulesService
