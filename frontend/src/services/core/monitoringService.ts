import { apiFactory } from './apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export class MonitoringService {
  async getPerformanceStats(endpoint?: string | null): Promise<ApiResponse<any>> {
    const params = endpoint ? { endpoint } : undefined
    return apiFactory.get<any>(API_ENDPOINTS.MONITORING.PERFORMANCE, { params })
  }

  async getPerformanceSummary(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MONITORING.PERFORMANCE_SUMMARY)
  }

  async resetPerformanceStats(): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.MONITORING.PERFORMANCE_RESET)
  }

  async getBenchmarkResults(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MONITORING.BENCHMARK)
  }

  async compareBenchmarks(name1: string, name2: string): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.MONITORING.BENCHMARK_COMPARE, null, {
      params: { name1, name2 }
    })
  }
}

export const monitoringService = new MonitoringService()