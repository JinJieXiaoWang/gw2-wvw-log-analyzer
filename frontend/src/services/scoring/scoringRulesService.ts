/**
 * 评分规则管理 API 服务
 */

import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'

export interface ScoringRule {
  id: number
  role_type: string
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
  rules: ScoringRule[]
}

export interface DimensionInfo {
  key: string
  label: string
}

class ScoringRulesService {
  /** 获取角色类型列表 */
  async getRoleTypes(): Promise<any[]> {
    const resp = await apiFactory.get<any[]>(API_ENDPOINTS.SCORING_RULES.ROLES)
    return resp.success && resp.data ? resp.data : []
  }

  /** 获取评分规则（按角色类型） */
  async getRules(roleType?: string): Promise<any> {
    const params: any = {}
    if (roleType) params.role_type = roleType
    const resp = await apiFactory.get(API_ENDPOINTS.SCORING_RULES.RULES, { params })
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

  /** 批量更新 */
  async batchUpdate(roleType: string, rules: Partial<ScoringRule>[]): Promise<any> {
    const resp = await apiFactory.post(API_ENDPOINTS.SCORING_RULES.BATCH, {
      role_type: roleType,
      rules,
    })
    return resp.success && resp.data ? resp.data : null
  }

  /** 重置为默认 */
  async resetDefault(roleType?: string): Promise<any> {
    const params: any = {}
    if (roleType) params.role_type = roleType
    const resp = await apiFactory.post(API_ENDPOINTS.SCORING_RULES.RESET, null, { params })
    return resp.success && resp.data ? resp.data : null
  }
}

export const scoringRulesService = new ScoringRulesService()
export default scoringRulesService
