/**
 * EI 分析摘要 API 服务（v2.1 增强版）
 * 对接 /api/v1/ei-analysis/{log_id}
 * 返回 ~15KB 战斗摘要（替代原先 40MB 完整 JSON）
 */

import { apiFactory, ApiResponse } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'

export interface EiAnalysisFight {
  id: number
  map_name: string
  start_time: string
  duration_sec: number
  duration_ms: number
  server_name: string
  recorded_by: string
  recorded_account: string
  total_damage: number
  total_healing: number
  kill_count: number
  death_count: number
  player_count: number
  is_wvw: boolean
}

export interface EiAnalysisPlayer {
  id: number
  member_id: number
  account: string
  character_name: string
  profession: string
  group_id: number
  has_commander_tag: boolean
  // 伤害
  damage: number
  dps: number
  power_damage: number
  condi_damage: number
  breakbar_damage: number
  // 命中质量
  critical_rate: number
  flanking_rate: number
  glance_rate: number
  missed: number
  interrupts: number
  swap_count: number
  // 击杀/控制
  killed: number
  down_count: number
  dead_count: number
  // 防御/生存
  damage_taken: number
  blocked_count: number
  evaded_count: number
  dodge_count: number
  // 支援
  boon_strips: number
  condition_cleanses: number
  resurrects: number
  condi_cleanse_ally: number
  boon_strips_ally: number
  healing: number
  // Buff 覆盖率
  might_uptime: number
  fury_uptime: number
  quickness_uptime: number
  alacrity_uptime: number
  protection_uptime: number
  stability_uptime: number
  // AI 评分
  ai_score: number
  score_grade: string
}

export interface EiAnalysisAggregate {
  duration_sec: number
  player_count: number
  total_damage: number
  total_power_damage: number
  total_condi_damage: number
  total_breakbar_damage: number
  total_damage_taken: number
  total_healing: number
  total_kills: number
  total_deaths: number
  total_downs: number
  total_boon_strips: number
  total_condition_cleanses: number
  total_resurrects: number
  avg_dps: number
  avg_critical_rate: number
}

export interface EiAnalysisEnemy {
  id: number
  member_id: number
  account: string
  character_name: string
  profession: string
  group_id: number
  has_commander_tag: boolean
  damage: number
  dps: number
  damage_taken: number
  critical_rate: number
  flanking_rate: number
  glance_rate: number
  missed: number
  down_count: number
  dead_count: number
}

export interface EiAnalysisResponse {
  log_id: number
  fight: EiAnalysisFight
  aggregate: EiAnalysisAggregate
  players: EiAnalysisPlayer[]
  total_players: number
  enemy_players: EiAnalysisEnemy[]
  profession_distribution: Record<string, number>
  buff_leaders: Record<string, EiAnalysisPlayer[]>
  support_leaders: Record<string, EiAnalysisPlayer[]>
  defense_leaders: Record<string, EiAnalysisPlayer[]>
  dps_report_permalink?: string
}

export interface SkillMapItem {
  name?: string
  icon?: string
  gw2_id: number
  skill_key: string
}

export interface PlayerRotationData {
  account: string
  character_name?: string
  profession?: string
  rotation: any[]
  skill_casts: Record<string, number>
  skill_map: Record<string, SkillMapItem>
  weapons: string[]
  death_recap: any[]
  consumables?: {
    food?: any[]
    utility?: any[]
  }
}

class EiAnalysisService {
  async getSummary(logId: number, sortBy: string = 'damage'): Promise<ApiResponse<EiAnalysisResponse>> {
    return apiFactory.get<EiAnalysisResponse>(API_ENDPOINTS.EI.ANALYSIS_SUMMARY(logId), {
      params: { sort_by: sortBy }
    })
  }

  async getPlayerDetail(logId: number, account: string): Promise<ApiResponse<EiAnalysisPlayer>> {
    return apiFactory.get<EiAnalysisPlayer>(API_ENDPOINTS.EI.ANALYSIS_PLAYER_DETAIL(logId, account))
  }

  async getPlayerRotation(logId: number, account: string): Promise<ApiResponse<PlayerRotationData>> {
    return apiFactory.get<PlayerRotationData>(API_ENDPOINTS.EI.ANALYSIS_PLAYER_ROTATION(logId, account))
  }
}

export const eiAnalysisService = new EiAnalysisService()
export default eiAnalysisService
