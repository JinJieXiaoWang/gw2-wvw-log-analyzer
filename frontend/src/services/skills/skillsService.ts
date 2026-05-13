import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface Skill {
  id: string
  name: string
  icon: string
  profession?: string
  elite_spec?: string
  type: 'heal' | 'utility' | 'elite' | 'weapon'
  description?: string
  cooldown?: number
  energy_cost?: number
  initiative_cost?: number
}

export interface SkillRotationEvent {
  timestamp: number
  skill_id: string
  skill_name: string
  target?: string
  success: boolean
}

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