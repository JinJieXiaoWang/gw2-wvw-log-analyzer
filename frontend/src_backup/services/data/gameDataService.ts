import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export class GameDataService {
  async getDataInfo(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.INFO)
  }

  async reloadData(): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.GAME_DATA.RELOAD)
  }

  async getProfessions(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.PROFESSIONS)
  }

  async getProfession(name: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.PROFESSION_DETAIL(name))
  }

  async getProfessionNameCn(name: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.PROFESSION_NAME_CN(name))
  }

  async getProfessionDefaultRole(name: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.PROFESSION_DEFAULT_ROLE(name))
  }

  async getProfessionScoringConfig(name: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.PROFESSION_SCORING_CONFIG(name))
  }

  async getEliteSpecs(baseProfession?: string | null): Promise<ApiResponse<any>> {
    const params = baseProfession ? { base_profession: baseProfession } : undefined
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.ELITE_SPECS, { params })
  }

  async getEliteSpec(name: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.ELITE_SPEC_DETAIL(name))
  }

  async getBuffs(category?: string | null, onlyKey: boolean = false): Promise<ApiResponse<any>> {
    const params: any = {}
    if (category) params.category = category
    if (onlyKey) params.only_key = true
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.BUFFS, { params })
  }

  async getBuff(buffId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.BUFF_DETAIL(buffId))
  }

  async getBuffNameCn(buffId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.BUFF_NAME_CN(buffId))
  }

  async getBuffCategories(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.GAME_DATA.BUFF_CATEGORIES)
  }
}

export const gameDataService = new GameDataService()