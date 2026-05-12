import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface FightsListParams {
  page?: number
  page_size?: number
  map_name?: string | null
  server_name?: string | null
}

export class FightsService {
  async getFights(params: FightsListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.FIGHTS.LIST, { params })
  }

  async getFight(fightId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.FIGHTS.DETAIL(fightId))
  }

  async getFightStats(fightId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.FIGHTS.STATS(fightId))
  }
}

export const fightsService = new FightsService()