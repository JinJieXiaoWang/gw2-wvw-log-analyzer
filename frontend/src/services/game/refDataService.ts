import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface RefDataItem {
  id: string
  name: string
  icon?: string
}

export interface RefDataListResponse {
  items: RefDataItem[]
  total: number
}

export class RefDataService {
  async getRunes(search?: string, limit: number = 100): Promise<ApiResponse<RefDataListResponse>> {
    return apiFactory.get<RefDataListResponse>(API_ENDPOINTS.REF_DATA.RUNES, {
      params: { search, limit }
    })
  }

  async getSigils(search?: string, limit: number = 100): Promise<ApiResponse<RefDataListResponse>> {
    return apiFactory.get<RefDataListResponse>(API_ENDPOINTS.REF_DATA.SIGILS, {
      params: { search, limit }
    })
  }

  async getRelics(search?: string, limit: number = 100): Promise<ApiResponse<RefDataListResponse>> {
    return apiFactory.get<RefDataListResponse>(API_ENDPOINTS.REF_DATA.RELICS, {
      params: { search, limit }
    })
  }

  async getFoods(search?: string, limit: number = 100): Promise<ApiResponse<RefDataListResponse>> {
    return apiFactory.get<RefDataListResponse>(API_ENDPOINTS.REF_DATA.FOODS, {
      params: { search, limit }
    })
  }

  async getUtilities(search?: string, limit: number = 100): Promise<ApiResponse<RefDataListResponse>> {
    return apiFactory.get<RefDataListResponse>(API_ENDPOINTS.REF_DATA.UTILITIES, {
      params: { search, limit }
    })
  }
}

export const refDataService = new RefDataService()
