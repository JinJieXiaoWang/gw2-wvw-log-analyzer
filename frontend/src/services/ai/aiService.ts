import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface ReportsListParams {
  page?: number
  page_size?: number
  report_type?: string | null
  target_type?: string | null
}

export class AIService {
  async getReports(params: ReportsListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.REPORTS, { params })
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

  async analyzeMemberSkills(memberId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_MEMBER(memberId))
  }

  async analyzeBuild(buildId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.ANALYZE_BUILD(buildId))
  }

  async getTrendAnalysis(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.TREND)
  }

  async getSuggestions(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.SUGGESTIONS)
  }
}

export const aiService = new AIService()