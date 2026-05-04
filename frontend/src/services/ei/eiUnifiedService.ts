/**
 * EI 统一数据 API 服务
 * 
 * 对接 /api/v1/ei-report/logs/{log_id}/unified
 * 自动选择最佳数据源（EI HTML 导入 或 ZEVTC 同步数据）
 */

import { apiFactory, ApiResponse } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'

// EI 统一数据响应结构
export interface EiUnifiedPlayer {
  instanceID: number
  name: string
  profession: string
  account: string
  group: number
  hasCommanderTag: boolean
  friendlyNPC: boolean
  notInSquad: boolean
  isFake: boolean
  dps: number
  total_score: number
  cc: number
  downs: number
  deaths: number
  cleanses: number
  strips: number
  weapons: string[]
  role: string
  hps: number
  critRate: number
  critDamage: number
  dpsAll: Array<{
    dps: number
    damage: number
    powerDamage: number
    condiDamage: number
    breakbarDamage: number
    actorDps: number
    actorDamage: number
    actorCondiDps: number
    actorCondiDamage: number
    actorPowerDps: number
    actorPowerDamage: number
    actorBreakbarDamage: number
  }>
  defenses: Array<{
    damageTaken: number
    downCount: number
    deadCount: number
    blockedCount: number
    evadedCount: number
    missedCount: number
    dodgeCount: number
    invulnedCount: number
    damageBarrier: number
    interruptedCount: number
    boonStrips: number
    conditionCleanses: number
  }>
  statsAll: Array<{
    criticalRate: number
    criticalDmg: number
    flankingRate: number
    againstMovingRate: number
    glanceRate: number
    missed: number
    evaded: number
    blocked: number
    interrupts: number
    invulned: number
    killed: number
    downed: number
    downContribution: number
    totalDamageCount: number
    directDamageCount: number
    connectedDirectDamageCount: number
    swapCount: number
    skillCastUptime: number
    skillCastUptimeNoAA: number
  }>
  support: Array<{
    condiCleanse: number
    boonStrips: number
  }>
  buffUptimes: Array<any>
  damage1S: number[][]
  powerDamage1S: number[][]
  conditionDamage1S: number[][]
  rotation: any[]
  damageModifiers: any[]
  totalDamageDist: any[]
  totalDamageTaken: any[]
  targetDamageDist: any[]
  statsTargets: any[]
  activeTimes: any[]
  selfBuffs: any[]
  buffUptimesActive: any[]
  selfBuffsActive: any[]
  healthPercents: any[]
  barrierPercents: any[]
  dpsTargets: any[]
  targetDamage1S: any[]
  targetPowerDamage1S: any[]
  targetConditionDamage1S: any[]
  totalHealth: number
  condition: number
  concentration: number
  healing: number
  toughness: number
  hitboxHeight: number
  hitboxWidth: number
  teamID: number
}

export interface EiUnifiedTarget {
  instanceID: number
  name: string
  icon: string
  finalHealth: number
  firstAware: number
  lastAware: number
  statsAll: Array<{ totalDmg: number }>
  dpsAll: Array<{ damage: number }>
  enemyPlayer: boolean
  totalHealth: number
  healthPercentBurned: number
  id: number
  condition: number
  concentration: number
  healing: number
  toughness: number
  hitboxHeight: number
  hitboxWidth: number
  teamID: number
  isFake: boolean
  buffs: any[]
  breakbarPercents: any[]
  defenses: any[]
  totalDamageDist: any[]
  totalDamageTaken: any[]
  damage1S: any[]
  powerDamage1S: any[]
  conditionDamage1S: any[]
}

export interface EiUnifiedPhase {
  name: string
  duration: number
  start: number
  end: number
  type: number
  nameNoMode: string
  icon: string
  mode: string
  encounterDuration: number
  startStatus: string
  success: boolean
  encounterPhase: boolean
  targets: number[]
  targetPriorities: Record<string, any>
  breakbarPhase: boolean
  breakbarRecovered: number
  breakbarStart: number
  subPhases: any[]
  markupLines: any[]
  markupAreas: any[]
}

export interface EiUnifiedLogData {
  duration: number
  evtcRecordingDuration: number
  logStart: string
  logEnd: string
  instanceStart: string
  instanceIP: string
  region: string
  arcVersion: string
  gw2Build: string
  triggerID: string
  logID: string
  mapID: string
  parser: string
  wvw: boolean
  hasCommander: boolean
  recordedBy: string
  recordedAccountBy: string
}

export interface EiUnifiedResponse {
  log_id: number
  source: 'ei_report' | 'zevtc_sync'
  fight_name: string
  duration_ms: number
  duration_str: string
  player_count: number
  target_count: number
  recorder: { name: string; account: string }
  versions: { eliteInsights: string; arc: string; gw2: string }
  log_data: EiUnifiedLogData
  players: EiUnifiedPlayer[]
  targets: EiUnifiedTarget[]
  phases: EiUnifiedPhase[]
  skill_map: Record<string, { name: string; id: number }>
  has_graph_data: boolean
  has_cr_data: boolean
}

class EiUnifiedService {
  /**
   * 获取统一的 EI 数据
   */
  async getUnifiedData(logId: number): Promise<ApiResponse<EiUnifiedResponse>> {
    return apiFactory.get<EiUnifiedResponse>(API_ENDPOINTS.EI.UNIFIED(logId))
  }
}

export { EiUnifiedService }
export const eiUnifiedService = new EiUnifiedService()
