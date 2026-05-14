import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'
import { apiFactory } from '../core/apiService'

export interface ReportsListParams {
  page?: number
  page_size?: number
  report_type?: string | null
  target_type?: string | null
}

export class AIService {
  async getReports(params: ReportsListParams): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.REPORTS, { params })
  }

  async getReport(reportId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.REPORT_DETAIL(reportId))
  }

  async deleteReport(reportId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.AI.REPORT_DETAIL(reportId))
  }

  async analyzeFight(fightId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_FIGHT(fightId))
  }

  async analyzeMemberSkills(memberId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.AI.ANALYZE_MEMBER(memberId))
  }

  async analyzeBuild(buildId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_BUILD(buildId))
  }

  async getTrendAnalysis(params?: { time_range?: string }): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.TREND, { params })
  }

  async getSuggestions(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.SUGGESTIONS)
  }

  async getStatus(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.STATUS)
  }

  async testConfiguration(): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.TEST)
  }

  async testConfigurationWithKey(provider: string, apiKey: string): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.TEST, null, {
      params: {
        provider,
        api_key: apiKey
      }
    })
  }

  async clearCache(): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.AI.CLEAR_CACHE)
  }

  // === 新增AI战术复盘与成长顾问系统 ===

  async analyzePersonalGrowth(account: string, fightCount: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_PERSONAL_GROWTH, null, {
      params: { account, fight_count: fightCount }
    })
  }

  async analyzeDeathAttribution(account: string, fightId?: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_DEATH_ATTRIBUTION, null, {
      params: { account, fight_id: fightId }
    })
  }

  async analyzeSquadSynergy(fightId: number, groupId?: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_SQUAD_SYNERGY, null, {
      params: { fight_id: fightId, group_id: groupId }
    })
  }

  async analyzeBuildExecution(account: string, buildId?: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_BUILD_EXECUTION, null, {
      params: { account, build_id: buildId }
    })
  }

  async analyzeCriticalMoments(fightId: number, account?: string): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_CRITICAL_MOMENTS, null, {
      params: { fight_id: fightId, account }
    })
  }
}

export const aiService = new AIService()