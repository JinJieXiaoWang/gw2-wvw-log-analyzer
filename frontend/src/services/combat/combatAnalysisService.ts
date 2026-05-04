/**
 * 战斗分析 API 服务
 * 功能：对接后端战斗分析接口，获取战斗数据
 * 作者：System
 * 创建日期：2026-04-29
 */

import { apiFactory, ApiResponse } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'

// 字段转换工具函数：snake_case -> camelCase
export function snakeToCamel(str: string): string {
  return str.replace(/(_\w)/g, (match) => match[1].toUpperCase())
}

// 递归转换对象属性名
export function convertKeysToCamelCase(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToCamelCase(item))
  }
  const result: Record<string, any> = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = snakeToCamel(key)
      result[newKey] = convertKeysToCamelCase(obj[key])
    }
  }
  return result
}

// 接口数据类型定义

export interface FightBasicInfo {
  map_name: string
  server_name: string
  total_damage: number
  total_healing: number
  kill_count: number
  death_count: number
  duration_sec: number
  start_time: string
  end_time: string
  is_wvw: boolean
  gw2_build: number
  duration_ms: number
  duration_str: string
  arc_version: string
  is_success: boolean
}

export interface FightDetailResponse {
  fight_id: number
  log_id: number
  basic_info: FightBasicInfo
}

export interface PlayerIdentifier {
  fight_stats_id: number
  instance_id: number
  member_id: number
  account_name: string
  member_name: string
}

export interface PlayerStatsSummary {
  damage: number
  healing: number
  dps: number
}

export interface PlayerListItem {
  member_id: number
  instance_id: number
  account_name: string
  member_name: string
  profession: string
  guild_tag: string
  fight_stats_id: number
  stats: {
    damage: number
    healing: number
    kills: number
    deaths: number
    time_in_combat: number
    damage_taken: number
    down_count: number
    res_count: number
    dps: number
    power_damage: number
    condi_damage: number
  }
}

export interface PlayersListResponse {
  players: PlayerListItem[]
  total?: number
}

export interface PlayerStatsDetail {
  damage: number
  healing: number
  kills: number
  deaths: number
  time_in_combat: number
  damage_taken: number
  down_count: number
  res_count: number
  dps: number
  power_damage: number
  condi_damage: number
  breakbar_damage: number
  interrupts: number
}

export interface PlayerStatsResponse {
  identifier: PlayerIdentifier
  stats: PlayerStatsDetail
}

export interface AmbiguousPlayer {
  fight_stats_id: number
  instance_id: number
  member_id: number
  account_name: string
  member_name: string
  profession: string
  guild_tag: string
  stats_summary: PlayerStatsSummary
}

export interface AmbiguousResponse {
  ambiguous: boolean
  message: string
  players: AmbiguousPlayer[]
  suggestion: string
}

export interface BuffUptime {
  [buffName: string]: number
}

export interface PlayerBuffsResponse {
  uptime_ms: BuffUptime
  uptime_percent: BuffUptime
}

export interface SkillBreakdown {
  [category: string]: number
}

export interface RotationSequenceItem {
  skill_id: number
  skill_name: string
  timestamp_ms: number
  duration_ms: number
}

export interface SkillFrequency {
  [skillName: string]: number
}

export interface PlayerRotationResponse {
  player_info: {
    instance_id: number
    member_name: string
    profession: string
  }
  duration_ms: number
  total_skills: number
  skill_breakdown: SkillBreakdown
  rotation_sequence: RotationSequenceItem[]
  skill_frequency: SkillFrequency
}

export interface LeaderboardRanking {
  rank: number
  member_id: number
  instance_id: number
  account_name: string
  member_name: string
  profession: string
  damage: number
  dps: number
  percentage: number
}

export interface LeaderboardResponse {
  total_damage: number
  top_damage_dealer: {
    member_name: string
    damage: number
    percentage: number
  }
  ranking: LeaderboardRanking[]
}

export interface TeamBuffProvider {
  avg_uptime_percent: number
  max_stack: number
  providers: string[]
}

export interface TeamBuffsResponse {
  duration_ms: number
  buff_summary: {
    [buffName: string]: TeamBuffProvider
  }
  missing_buffs: string[]
}

// 查询参数类型
export interface PlayersListParams {
  sort_by?: 'damage' | 'dps' | 'kills' | 'deaths'
  order?: 'asc' | 'desc'
}

export interface PlayerQueryParams {
  fight_stats_id?: number
  instance_id?: number
  account_name?: string
  member_name?: string
}

export interface RotationParams {
  fight_stats_id?: number
  instance_id?: number
  account_name?: string
  member_name?: string
  output_format?: 'json' | 'summary' | 'detailed'
}

class CombatAnalysisService {
  /**
   * 获取战斗基础信息
   */
  async getFightBasic(logId: number): Promise<ApiResponse<FightDetailResponse>> {
    try {
      const response = await apiFactory.get<FightDetailResponse>(API_ENDPOINTS.COMBAT_ANALYSIS.FIGHT_BASIC(logId))
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取战斗基础信息失败:', error)
      throw error
    }
  }

  /**
   * 获取战斗详情（完整信息）
   */
  async getFightDetail(logId: number): Promise<ApiResponse<any>> {
    try {
      const response = await apiFactory.get<any>(API_ENDPOINTS.COMBAT_ANALYSIS.FIGHT_DETAILS(logId))
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取战斗详情失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家列表
   */
  async getPlayersList(logId: number, params?: PlayersListParams): Promise<ApiResponse<PlayersListResponse>> {
    try {
      const response = await apiFactory.get<PlayersListResponse>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYERS_LIST(logId),
        { params }
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家列表失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家统计信息（推荐方式）
   */
  async getPlayerStats(
    logId: number,
    params: PlayerQueryParams
  ): Promise<ApiResponse<PlayerStatsResponse | AmbiguousResponse>> {
    try {
      const response = await apiFactory.get<PlayerStatsResponse | AmbiguousResponse>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYER_STATS(logId),
        { params }
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家统计失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家详情（向后兼容）
   */
  async getPlayerDetailLegacy(logId: number, accountName: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiFactory.get<any>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYER_DETAIL_LEGACY(logId, accountName)
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家详情失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家 Buff 数据（推荐方式）
   */
  async getPlayerBuffs(
    logId: number,
    params: PlayerQueryParams
  ): Promise<ApiResponse<PlayerBuffsResponse | AmbiguousResponse>> {
    try {
      const response = await apiFactory.get<PlayerBuffsResponse | AmbiguousResponse>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYER_BUFFS(logId),
        { params }
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家 Buff 数据失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家 Buff 数据（向后兼容）
   */
  async getPlayerBuffsLegacy(logId: number, accountName: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiFactory.get<any>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYER_BUFFS_LEGACY(logId, accountName)
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家 Buff 数据失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家技能循环（推荐方式）
   */
  async getPlayerRotation(
    logId: number,
    params: RotationParams
  ): Promise<ApiResponse<PlayerRotationResponse | AmbiguousResponse>> {
    try {
      const response = await apiFactory.get<PlayerRotationResponse | AmbiguousResponse>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYER_ROTATION(logId),
        { params }
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家技能循环失败:', error)
      throw error
    }
  }

  /**
   * 获取玩家技能循环（向后兼容）
   */
  async getPlayerRotationLegacy(logId: number, accountName: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiFactory.get<any>(
        API_ENDPOINTS.COMBAT_ANALYSIS.PLAYER_ROTATION_LEGACY(logId, accountName)
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取玩家技能循环失败:', error)
      throw error
    }
  }

  /**
   * 获取团队 Buff 汇总
   */
  async getTeamBuffs(logId: number): Promise<ApiResponse<TeamBuffsResponse>> {
    try {
      const response = await apiFactory.get<TeamBuffsResponse>(
        API_ENDPOINTS.COMBAT_ANALYSIS.TEAM_BUFFS(logId)
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取团队 Buff 汇总失败:', error)
      throw error
    }
  }

  /**
   * 获取排行榜数据
   */
  async getLeaderboard(logId: number): Promise<ApiResponse<LeaderboardResponse>> {
    try {
      const response = await apiFactory.get<LeaderboardResponse>(
        API_ENDPOINTS.COMBAT_ANALYSIS.LEADERBOARD(logId)
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取排行榜数据失败:', error)
      throw error
    }
  }

  /**
   * 获取原始解析数据
   */
  async getRawData(logId: number): Promise<ApiResponse<any>> {
    try {
      const response = await apiFactory.get<any>(
        API_ENDPOINTS.COMBAT_ANALYSIS.RAW_DATA(logId)
      )
      return response
    } catch (error) {
      console.error('[CombatAnalysisService] 获取原始解析数据失败:', error)
      throw error
    }
  }

  /**
   * 检查响应是否为歧义响应
   */
  isAmbiguousResponse(response: any): response is AmbiguousResponse {
    return response && response.ambiguous === true
  }

  /**
   * 根据日志状态检查是否可以访问数据
   */
  async checkLogStatus(logId: number): Promise<{ canAccess: boolean; message?: string }> {
    try {
      const response = await this.getFightBasic(logId)
      if (!response.success) {
        return { canAccess: false, message: response.message }
      }
      return { canAccess: true }
    } catch (error: any) {
      if (error.response?.data?.message) {
        return { canAccess: false, message: error.response.data.message }
      }
      return { canAccess: false, message: '无法检查日志状态' }
    }
  }
}

export { CombatAnalysisService }
export const combatAnalysisService = new CombatAnalysisService()
