/**
 * 数据看板 API
 * 功能：获取统计数据、趋势图、分布图等
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { HttpClient } from '../../services/core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'

export interface DashboardOverview {
  totalLogs: number
  totalPlayers: number
  totalMaps: number
  totalServers: number
  recentActivity: Array<{
    type: string
    message: string
    time: string
  }>
}

export interface TrendData {
  date: string
  value: number
  label: string
}

export interface DistributionData {
  name: string
  value: number
  color?: string
}

export interface DashboardStats {
  overview: DashboardOverview
  weeklyTrend: TrendData[]
  professionDistribution: DistributionData[]
  mapDistribution: DistributionData[]
  serverDistribution: DistributionData[]
}

class DashboardApi {
  /**
   * 获取概览数据
   */
  async getOverview() {
    return await HttpClient.get<DashboardOverview>(API_ENDPOINTS.DASHBOARD.STATS)
  }

  /**
   * 获取完整统计数据
   */
  async getStats(params?: { dateRange?: string }) {
    return await HttpClient.get<DashboardStats>(API_ENDPOINTS.DASHBOARD.STATS, { params })
  }

  /**
   * 获取趋势数据
   */
  async getTrends(params?: { days?: number; type?: string }) {
    return await HttpClient.get<TrendData[]>('/api/v1/dashboard/trends', { params })
  }

  /**
   * 获取地图统计
   */
  async getMapStats() {
    return await HttpClient.get<DistributionData[]>('/api/v1/dashboard/maps')
  }
}

export const dashboardApi = new DashboardApi()
export default dashboardApi
