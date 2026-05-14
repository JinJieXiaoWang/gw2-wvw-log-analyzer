import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '../../models'
import { apiFactory } from '../core/apiService'

export interface AiReport {
  id: string | number
  report_type: string
  target_type: string
  target_id: number
  summary?: string
  ai_score?: number
  created_at: string
  content?: string
  metadata?: Record<string, unknown>
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
  type?: string | undefined
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

  async getTrendAnalysis(params?: { time_range?: string }): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.TREND, { params })
  }

  async getSuggestions(): Promise<ApiResponse<unknown>> {
    return apiFactory.get<unknown>(API_ENDPOINTS.AI.SUGGESTIONS)
  }

  async getStatus(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AI.STATUS)
  }

  async testConfiguration(): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.AI.TEST)
  }

  async clearCache(): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.AI.CLEAR_CACHE)
  }
}

export const aiService = new AIService()