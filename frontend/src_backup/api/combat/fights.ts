/**
 * 战斗数据 API
 * 功能：处理战斗列表、战斗详情、战斗统计数据等
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { HttpClient } from '../../services/core/apiService'

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

class FightsApi {
  /**
   * 获取战斗列表
   */
  async getFights(params?: FightQueryParams) {
    return await HttpClient.get<Fight[]>('/api/v1/fights', { params })
  }

  /**
   * 获取战斗详情
   */
  async getFightDetail(id: string) {
    return await HttpClient.get<Fight>(`/api/v1/fights/${id}`)
  }

  /**
   * 获取战斗统计数据
   */
  async getFightStats(id: string) {
    return await HttpClient.get<FightStats>(`/api/v1/fights/${id}/stats`)
  }
}

export const fightsApi = new FightsApi()
export default fightsApi