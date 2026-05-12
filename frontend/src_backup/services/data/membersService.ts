import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface MembersListParams {
  page?: number
  page_size?: number
  profession?: string | null
  guild_tag?: string | null
}

export interface MemberRankingParams {
  page?: number
  page_size?: number
  sort_by?: string
}

export class MembersService {
  async getMembers(params: MembersListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MEMBERS.LIST, { params })
  }

  async getMemberRanking(params: MemberRankingParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MEMBERS.RANKING, { params })
  }

  async getProfessionDistribution(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MEMBERS.PROFESSIONS)
  }

  async getMember(memberId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MEMBERS.DETAIL(memberId))
  }

  async getMemberStats(memberId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.MEMBERS.STATS(memberId))
  }
}

export const membersService = new MembersService()