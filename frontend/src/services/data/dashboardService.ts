import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export class DashboardService {
  async getOverview(days: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.DASHBOARD.OVERVIEW, {
      params: { days }
    })
  }

  async getTrends(days: number = 30, metric: string = 'damage'): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.DASHBOARD.TRENDS, {
      params: { days, metric }
    })
  }

  async getDashboardStats(days: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.DASHBOARD.STATS, {
      params: { days }
    })
  }

  async getProfessionDistribution(days: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.DASHBOARD.PROFESSION_DISTRIBUTION, {
      params: { days }
    })
  }

  async getMapStatistics(days: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.DASHBOARD.MAPS, {
      params: { days }
    })
  }

  async getTopPlayers(
    days: number = 30,
    sortBy: string = 'damage',
    limit: number = 20
  ): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(`${API_ENDPOINTS.DASHBOARD.BASE}/top-players`, {
      params: { days, sort_by: sortBy, limit }
    })
  }

  async getRecentFights(limit: number = 10): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(`${API_ENDPOINTS.DASHBOARD.BASE}/recent-fights`, {
      params: { limit }
    })
  }

  async getParseStatus(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(`${API_ENDPOINTS.DASHBOARD.BASE}/parse-status`)
  }

  async getAiScoreDistribution(days: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(`${API_ENDPOINTS.DASHBOARD.BASE}/ai-score-distribution`, {
      params: { days }
    })
  }

  async getBuffOverview(days: number = 30): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(`${API_ENDPOINTS.DASHBOARD.BASE}/buff-overview`, {
      params: { days }
    })
  }
}

export const dashboardService = new DashboardService()
