import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface SkillsListParams {
  page?: number
  page_size?: number
  profession?: string | null
}

export class SkillsService {
  async getSkills(params: SkillsListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SKILLS.LIST, { params })
  }

  async getSkill(skillId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SKILLS.DETAIL(skillId))
  }

  async getSkillEvents(fightId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SKILLS.FIGHT_EVENTS(fightId))
  }

  async getMemberRotation(memberId: number, fightId?: number | null): Promise<ApiResponse<any>> {
    const params = fightId ? { fight_id: fightId } : undefined
    return apiFactory.get<any>(API_ENDPOINTS.SKILLS.MEMBER_ROTATION(memberId), { params })
  }
}

export const skillsService = new SkillsService()