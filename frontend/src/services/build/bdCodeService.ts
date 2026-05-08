import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface BDCodeParseRequest {
  bd_code: string
  include_icons?: boolean
}

export interface BDCodeValidationRequest {
  bd_code: string
}

export interface BDCodeBatchRequest {
  bd_codes: string[]
  include_icons?: boolean
}

export class BDCodeService {
  async parseBDCode(data: BDCodeParseRequest): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.PARSE, data)
  }

  async parseBDCodeByUrl(bdCode: string, includeIcons: boolean = true): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.PARSE_BY_URL(bdCode), {
      params: { include_icons: includeIcons }
    })
  }

  async validateBDCode(data: BDCodeValidationRequest): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.VALIDATE, data)
  }

  async parseBatch(data: BDCodeBatchRequest): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.BATCH, data)
  }

  async getBDCodeStats(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.STATS)
  }

  async healthCheck(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.HEALTH)
  }
}

export const bdCodeService = new BDCodeService()