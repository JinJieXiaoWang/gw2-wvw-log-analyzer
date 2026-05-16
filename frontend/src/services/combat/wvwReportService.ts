/**
 * WvW 战斗报告 API 服务
 * 功能：对接后端 WvW Report 接口，获取 ZEVTC 同步的 EI 格式分析数据
 * 设计理念：
 *   - 聚焦 WvW 场景核心需求
 *   - 提供 squad composition、performance ranking、timeline 等差异化功能
 */

import { apiFactory, ApiResponse } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import { convertKeysToCamelCase } from '@/utils/core/caseConverter'

// =====================================================================
// 数据类型定义
// =====================================================================

export interface WvwReportListItem {
  logId: number
  logName: string
  durationMs: number
  durationSec: number
  playerCount: number
  uploadedAt: string
}

export interface WvwReportListResponse {
  total: number
  items: WvwReportListItem[]
  page: number
  page_size: number
}

export interface WvwPlayersData {
  count: number
  players: WvwPlayerSummary[]
}

export interface WvwTimelineData {
  count: number
  events: WvwTimelineEvent[]
}

export interface WvwTargetsData {
  count: number
  targets: any[]
}

export interface WvwPhasesData {
  count: number
  phases: any[]
}

export interface WvwSkillMapData {
  count: number
  skills: Record<string, any>
}

export interface WvwDamageSummary {
  total: number
  power: number
  condi: number
  avgDps: number
}

export interface WvwDefensesSummary {
  totalDown: number
  totalDead: number
  totalDamageTaken: number
}

export interface WvwSupportSummary {
  totalCleanse: number
  totalHealing: number
}

export interface WvwProfessionComposition {
  name: string
  count: number
  damage: number
}

export interface WvwGroupComposition {
  groupId: number
  count: number
}

export interface WvwPhaseSummary {
  phaseIndex: number
  name: string
  startMs: number
  endMs: number
  durationMs: number
}

export interface WvwSummaryResponse {
  logId: number
  logName: string
  arcVersion: string | null
  durationMs: number
  durationSec: number
  playerCount: number
  targetCount: number
  uploadedAt: string | null
  damage: WvwDamageSummary
  defenses: WvwDefensesSummary
  support: WvwSupportSummary
  composition: {
    professions: WvwProfessionComposition[]
    groups: WvwGroupComposition[]
  }
  phases: WvwPhaseSummary[]
  hasSyncedData: boolean
}

export interface WvwPlayerSummary {
  playerId: number
  agentIndex: number | null
  account: string | null
  characterName: string
  profession: string
  groupId: number
  hasCommanderTag: boolean
  damage: number
  dps: number
  powerDamage: number
  condiDamage: number
  criticalRate: number
  flankingRate: number
  missed: number
  glanceRate: number
  swapCount: number
  damageTaken: number
  downCount: number
  deadCount: number
  condiCleanse: number
  healing: number
  rotationLength: number
}

export interface WvwPlayersResponse {
  count: number
  players: WvwPlayerSummary[]
}

export interface WvwPlayerDetail {
  playerId: number
  agentIndex: number | null
  account: string | null
  characterName: string
  profession: string
  groupId: number | null
  hasCommanderTag: boolean
  dpsAll: any[]
  statsAll: any[]
  defenses: any[]
  support: any[]
  buffUptimes: any[]
  rotation: any[]
}

export interface WvwTimelineEvent {
  timeMs: number
  eventType: string
  agentInstid: number
  agentName: string
  skillId: number
}

export interface WvwTimelineResponse {
  count: number
  events: WvwTimelineEvent[]
}

// =====================================================================
// 服务类
// =====================================================================

class WvwReportService {
  /**
   * 获取有同步数据的日志列表
   */
  async getLogs(page: number = 1, pageSize: number = 20): Promise<ApiResponse<WvwReportListResponse>> {
    const response = await apiFactory.get<WvwReportListResponse>(API_ENDPOINTS.WVW_REPORT.LOGS, {
      params: { page, page_size: pageSize }
    })
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取战斗概览
   */
  async getSummary(logId: number): Promise<ApiResponse<WvwSummaryResponse>> {
    const response = await apiFactory.get<WvwSummaryResponse>(API_ENDPOINTS.WVW_REPORT.SUMMARY(logId))
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取玩家排行榜
   */
  async getPlayers(
    logId: number,
    sortBy: string = 'damage'
  ): Promise<ApiResponse<WvwPlayersData>> {
    const response = await apiFactory.get<WvwPlayersData>(API_ENDPOINTS.WVW_REPORT.PLAYERS(logId), {
      params: { sort_by: sortBy }
    })
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取单个玩家详情
   */
  async getPlayerDetail(
    logId: number,
    playerId: number
  ): Promise<ApiResponse<WvwPlayerDetail>> {
    const response = await apiFactory.get<WvwPlayerDetail>(API_ENDPOINTS.WVW_REPORT.PLAYER_DETAIL(logId, playerId))
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取目标列表
   */
  async getTargets(logId: number): Promise<ApiResponse<any>> {
    const response = await apiFactory.get<any>(API_ENDPOINTS.WVW_REPORT.TARGETS(logId))
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取阶段列表
   */
  async getPhases(logId: number): Promise<ApiResponse<any>> {
    const response = await apiFactory.get<any>(API_ENDPOINTS.WVW_REPORT.PHASES(logId))
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取战斗时间线
   */
  async getTimeline(logId: number): Promise<ApiResponse<WvwTimelineData>> {
    const response = await apiFactory.get<WvwTimelineData>(API_ENDPOINTS.WVW_REPORT.TIMELINE(logId))
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }

  /**
   * 获取技能映射表
   */
  async getSkillMap(logId: number): Promise<ApiResponse<any>> {
    const response = await apiFactory.get<any>(API_ENDPOINTS.WVW_REPORT.SKILL_MAP(logId))
    if (response.success && response.data) {
      response.data = convertKeysToCamelCase(response.data)
    }
    return response
  }
}

export { WvwReportService }
export const wvwReportService = new WvwReportService()
