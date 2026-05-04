/**
 * AI分析 API
 * 功能：处理AI报告、AI分析、AI趋势、AI优化建议等
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { HttpClient } from '../../services/core/apiService'

export interface AiReport {
  id: string
  type: string
  targetType: string
  targetId: string
  targetName: string
  analysis: any
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

export interface AiAnalysisResult {
  id: string
  type: string
  targetId: string
  targetName: string
  results: any
  suggestions: AiSuggestion[]
  createdAt: string
}

export interface AiReportQueryParams {
  page?: number
  pageSize?: number
  reportType?: string
  targetType?: string
  startDate?: string
  endDate?: string
}

class AiApi {
  /**
   * 获取AI报告列表
   */
  async getReports(params?: AiReportQueryParams) {
    return await HttpClient.get<AiReport[]>('/api/v1/ai/reports', { params })
  }

  /**
   * 获取AI报告详情
   */
  async getReportDetail(id: string) {
    return await HttpClient.get<AiReport>(`/api/v1/ai/reports/${id}`)
  }

  /**
   * 删除AI报告
   */
  async deleteReport(id: string) {
    return await HttpClient.delete<void>(`/api/v1/ai/reports/${id}`)
  }

  /**
   * AI分析战斗
   */
  async analyzeFight(fightId: string) {
    return await HttpClient.post<AiAnalysisResult>(`/api/v1/ai/analyze/fight/${fightId}`)
  }

  /**
   * AI分析成员技能循环
   */
  async analyzeMember(memberId: string) {
    return await HttpClient.post<AiAnalysisResult>(`/api/v1/ai/analyze/member/${memberId}`)
  }

  /**
   * AI分析Build
   */
  async analyzeBuild(buildId: string) {
    return await HttpClient.post<AiAnalysisResult>(`/api/v1/ai/analyze/build/${buildId}`)
  }

  /**
   * 获取AI趋势分析
   */
  async getTrend() {
    return await HttpClient.get<AiTrend[]>('/api/v1/ai/trend')
  }

  /**
   * 获取AI优化建议
   */
  async getSuggestions() {
    return await HttpClient.get<AiSuggestion[]>('/api/v1/ai/suggestions')
  }
}

export const aiApi = new AiApi()
export default aiApi