import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface SettingsUpdate {
  theme?: string
  language?: string
  timezone?: string
  [key: string]: any
}

export class SettingsService {
  async getSettings(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SETTINGS.GET)
  }

  async updateSettings(data: SettingsUpdate): Promise<ApiResponse<any>> {
    return apiFactory.put<any>(API_ENDPOINTS.SETTINGS.UPDATE, data)
  }

  async resetSettings(): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.SETTINGS.RESET)
  }
}

export const settingsService = new SettingsService()