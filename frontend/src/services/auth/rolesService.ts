import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'
import type { ApiResponse } from '../../models'

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
  rules?: any[]
  templates?: any[]
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
  async getAllRules(includeInactive: boolean = false): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.RULES, {
      params: { include_inactive: includeInactive }
    })
  }

  async createRule(data: RoleRuleCreate): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.ROLES.RULES, data)
  }

  async getProfessionRules(professionId: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.RULES_BY_PROFESSION(professionId))
  }

  async getRule(ruleId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.RULE_DETAIL(ruleId))
  }

  async updateRule(ruleId: number, data: RoleRuleUpdate): Promise<ApiResponse<any>> {
    return apiFactory.put<any>(API_ENDPOINTS.ROLES.RULE_UPDATE(ruleId), data)
  }

  async deleteRule(ruleId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.ROLES.RULE_DELETE(ruleId))
  }

  async getAllTemplates(includeInactive: boolean = false): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.TEMPLATES, {
      params: { include_inactive: includeInactive }
    })
  }

  async createTemplate(data: RoleTemplateCreate): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.ROLES.TEMPLATES, data)
  }

  async getTemplate(templateId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.TEMPLATE_DETAIL(templateId))
  }

  async updateTemplate(templateId: number, data: RoleTemplateUpdate): Promise<ApiResponse<any>> {
    return apiFactory.put<any>(API_ENDPOINTS.ROLES.TEMPLATE_UPDATE(templateId), data)
  }

  async deleteTemplate(templateId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.ROLES.TEMPLATE_DELETE(templateId))
  }

  async getTemplateByName(templateName: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.TEMPLATE_BY_NAME(templateName))
  }

  async applyTemplate(templateId: number, data: TemplateApplyRequest): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.ROLES.TEMPLATE_APPLY(templateId), data)
  }

  async initPresetTemplates(): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.ROLES.TEMPLATE_INIT_PRESETS)
  }

  async exportData(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.EXPORT)
  }

  async importData(data: ImportDataRequest): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.ROLES.IMPORT, data)
  }

  async getAllExpressions(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.EXPRESSIONS)
  }

  async createExpression(data: ConditionExpressionCreate): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.ROLES.EXPRESSIONS, data)
  }

  async assignRole(data: RoleAssignmentRequest): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.ROLES.ASSIGN, data)
  }

  async queryRoles(professionId?: string | null, roleTag?: string | null, includeInactive: boolean = false): Promise<ApiResponse<any>> {
    const params: any = { include_inactive: includeInactive }
    if (professionId) params.profession_id = professionId
    if (roleTag) params.role_tag = roleTag
    return apiFactory.get<any>(API_ENDPOINTS.ROLES.QUERY, { params })
  }
}

export const rolesService = new RolesService()