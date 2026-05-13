import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface AiReport {
  id: string
  type: string
  targetType: string
  targetId: string
  targetName: string
  analysis: unknown
  createdAt: string
  updatedAt: string
}

export interface AiTrend {
  period: string
  metrics: {
    averagePerformance: number
    totalFights: number
    averageDuration: number
    winRate: number
  }
}

export interface AiSuggestion {
  id: string
  type: string
  priority: 'low' | 'medium' | 'high'
  title: string
  description: string
  recommendation: string
  impact: string
  relatedMetrics: string[]
}

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

  async getReport(reportId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.REPORT_DETAIL(reportId))
  }

  async deleteReport(reportId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.AI.REPORT_DETAIL(reportId))
  }

  async analyzeFight(fightId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.AI.ANALYZE_FIGHT(fightId))
  }

  async analyzeMemberSkills(memberId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.AI.ANALYZE_MEMBER(memberId))
  }

  async analyzeBuild(buildId: number): Promise<ApiResponse<unknown>> {
    return apiFactory.post<unknown>(API_ENDPOINTS.AI.ANALYZE_BUILD(buildId))
  }

  async getTrendAnalysis(): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.TREND)
  }

  async getSuggestions(): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.SUGGESTIONS)
  }
}

export const aiService = new AIService()