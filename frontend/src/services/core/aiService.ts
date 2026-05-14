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

  async getTrendAnalysis(): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.TREND)
  }

  async getSuggestions(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.SUGGESTIONS)
  }

  async getStatus(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.STATUS)
  }

  async testConfiguration(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.TEST)
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
}

export const aiService = new AIService()