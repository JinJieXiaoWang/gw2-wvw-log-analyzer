import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface SkillRotationAnalyzeRequest {
  member_account: string
  fight_id?: number
  granularity?: string
  output_format?: string
}

export class SkillRotationService {
  async healthCheck(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SKILL_ROTATION.HEALTH)
  }

  async getPlayerSkillRotation(memberAccount: string, fightId?: number | null, granularity: string = 'detailed', outputFormat: string = 'json'): Promise<ApiResponse<any>> {
    const params: any = { granularity, output_format: outputFormat }
    if (fightId) params.fight_id = fightId
    return apiFactory.get<any>(API_ENDPOINTS.SKILL_ROTATION.PLAYER(memberAccount), { params })
  }

  async analyzeSkillRotation(data: SkillRotationAnalyzeRequest): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.SKILL_ROTATION.ANALYZE, data)
  }

  async getErrorCodes(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SKILL_ROTATION.ERRORS)
  }

  async compareSkillRotation(memberAccount: string, benchmarkAccount: string, fightId?: number | null): Promise<ApiResponse<any>> {
    const params: any = { benchmark_account: benchmarkAccount }
    if (fightId) params.fight_id = fightId
    return apiFactory.get<any>(API_ENDPOINTS.SKILL_ROTATION.COMPARE_PLAYER(memberAccount), { params })
  }

  async analyzeSkillRotationByIds(logId: string, memberId: string): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.SKILL_ROTATION.ANALYZE, { log_id: logId, member_id: memberId })
  }

  async exportReport(logId: string, memberId: string): Promise<any | null> {
    const response = await apiFactory.post<ApiResponse<any>>(
      API_ENDPOINTS.SKILL_ROTATION.EXPORT_REPORT,
      { log_id: logId, member_id: memberId }
    )
    if (response.success && response.data) {
      return response.data
    }
    return null
  }
}

export const skillRotationService = new SkillRotationService()