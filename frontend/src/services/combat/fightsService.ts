import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface Fight {
  id: string
  logId: string
  mapName: string
  serverName: string
  startTime: string
  endTime: string
  duration: number
  playerCount: number
  result: 'win' | 'loss' | 'draw'
  objectives: Array<{
    id: string
    name: string
    type: string
    captured: boolean
    timestamp: string
  }>
  createdAt: string
  updatedAt: string
}

export interface FightStats {
  fightId: string
  totalDamage: number
  totalDamageTaken: number
  totalDeaths: number
  totalKills: number
  totalDowned: number
  averageDamage: number
  winRate: number
  playerStats: Array<{
    accountName: string
    profession: string
    damage: number
    damageTaken: number
    deaths: number
    kills: number
    downed: number
    revived: number
  }>
}

export interface FightQueryParams {
  page?: number
  pageSize?: number
  mapName?: string
  serverName?: string
  startDate?: string
  endDate?: string
  result?: 'win' | 'loss' | 'draw'
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

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