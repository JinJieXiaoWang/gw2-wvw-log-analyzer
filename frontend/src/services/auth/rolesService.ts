import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface RoleRuleCreate {
  profession_id: string
  role_tag: string
  role_name: string
  description?: string
  priority?: number
  is_active?: boolean
}

export interface RoleRuleUpdate {
  role_tag?: string
  role_name?: string
  description?: string
  priority?: number
  is_active?: boolean
}

export interface RoleTemplateCreate {
  template_name: string
  description?: string
  is_active?: boolean
}

export interface RoleTemplateUpdate {
  template_name?: string
  description?: string
  is_active?: boolean
}

export interface TemplateApplyRequest {
  profession_ids: string[]
}

export interface ImportDataRequest {
  rules?: unknown[]
  templates?: unknown[]
}

export interface ConditionExpressionCreate {
  expression_name: string
  expression_type: string
  expression_value: string
  description?: string
}

export interface RoleAssignmentRequest {
  profession_id: string
  role_tag: string
}

export class RolesService {
  async getAllRules(includeInactive: boolean = false): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.RULES, {
      params: { include_inactive: includeInactive }
    })
  }

  async createRule(data: RoleRuleCreate): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.ROLES.RULES, data)
  }

  async getProfessionRules(professionId: string): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.RULES_BY_PROFESSION(professionId))
  }

  async getRule(ruleId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.RULE_DETAIL(ruleId))
  }

  async updateRule(ruleId: number, data: RoleRuleUpdate): Promise<ApiResponse<unknown>> {
    return apiFactory.put<unknown>(API_ENDPOINTS.ROLES.RULE_UPDATE(ruleId), data)
  }

  async deleteRule(ruleId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.ROLES.RULE_DELETE(ruleId))
  }

  async getAllTemplates(includeInactive: boolean = false): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.TEMPLATES, {
      params: { include_inactive: includeInactive }
    })
  }

  async createTemplate(data: RoleTemplateCreate): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.ROLES.TEMPLATES, data)
  }

  async getTemplate(templateId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.TEMPLATE_DETAIL(templateId))
  }

  async updateTemplate(templateId: number, data: RoleTemplateUpdate): Promise<ApiResponse<unknown>> {
    return apiFactory.put<unknown>(API_ENDPOINTS.ROLES.TEMPLATE_UPDATE(templateId), data)
  }

  async deleteTemplate(templateId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.ROLES.TEMPLATE_DELETE(templateId))
  }

  async getTemplateByName(templateName: string): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.TEMPLATE_BY_NAME(templateName))
  }

  async applyTemplate(templateId: number, data: TemplateApplyRequest): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.ROLES.TEMPLATE_APPLY(templateId), data)
  }

  async initPresetTemplates(): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.ROLES.TEMPLATE_INIT_PRESETS)
  }

  async exportData(): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.EXPORT)
  }

  async importData(data: ImportDataRequest): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.ROLES.IMPORT, data)
  }

  async getAllExpressions(): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.EXPRESSIONS)
  }

  async createExpression(data: ConditionExpressionCreate): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.ROLES.EXPRESSIONS, data)
  }

  async assignRole(data: RoleAssignmentRequest): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.ROLES.ASSIGN, data)
  }

  async queryRoles(professionId?: string | null, roleTag?: string | null, includeInactive: boolean = false): Promise<ApiResponse<any>> {
    const params: Record<string, unknown> = { include_inactive: includeInactive }
    if (professionId) params.profession_id = professionId
    if (roleTag) params.role_tag = roleTag
    return apiFactory.get<unknown>(API_ENDPOINTS.ROLES.QUERY, { params })
  }
}

export const rolesService = new RolesService()