/**
 * 战斗统计数据常量与计算工具
 * 功能：统计分类定义、字段映射、数值提取、小队统计计算
 */

import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'

/** 统计分类类型 */
export type StatCategory =
  | 'protection' | 'stability' | 'condition_cleanses' | 'boon_strips'
  | 'damage_taken' | 'hitRate' | 'damage_output' | 'hit_quality'
  | 'buff_coverage' | 'survival' | 'support' | 'control' | 'efficiency' | 'position'

/** 分类排序主键映射 */
export const CATEGORY_SORT_KEY: Record<StatCategory, keyof EiAnalysisPlayer> = {
  protection: 'protection_uptime',
  stability: 'stability_uptime',
  condition_cleanses: 'condition_cleanses',
  boon_strips: 'boon_strips',
  damage_taken: 'damage_taken',
  hitRate: 'missed',
  damage_output: 'damage',
  hit_quality: 'critical_rate',
  buff_coverage: 'might_uptime',
  survival: 'damage_taken',
  support: 'boon_strips',
  control: 'downed',
  efficiency: 'skill_cast_uptime',
  position: 'stack_dist',
}

/** 分类字段与标签定义 */
export const CATEGORY_FIELDS: Record<StatCategory, { fields: string[]; labels: Record<string, string> }> = {
  protection: { fields: ['protection_uptime'], labels: { protection_uptime: '保护覆盖率' } },
  stability: { fields: ['stability_uptime'], labels: { stability_uptime: '稳固覆盖率' } },
  condition_cleanses: { fields: ['condition_cleanses'], labels: { condition_cleanses: '清症次数' } },
  boon_strips: { fields: ['boon_strips'], labels: { boon_strips: '削增益次数' } },
  damage_taken: { fields: ['damage_taken'], labels: { damage_taken: '承受伤害' } },
  hitRate: { fields: ['hitRate'], labels: { hitRate: '命中率' } },
  damage_output: {
    fields: ['damage', 'dps', 'power_damage', 'condi_damage', 'breakbar_damage'],
    labels: { damage: '总伤害', dps: 'DPS', power_damage: '直伤', condi_damage: '症状', breakbar_damage: '破甲' }
  },
  hit_quality: {
    fields: ['critical_rate', 'flanking_rate', 'glance_rate', 'missed', 'interrupts'],
    labels: { critical_rate: '暴击次数', flanking_rate: '背击次数', glance_rate: '偏斜次数', missed: '未命中', interrupts: '打断' }
  },
  buff_coverage: {
    fields: ['might_uptime', 'fury_uptime', 'quickness_uptime', 'alacrity_uptime', 'protection_uptime', 'stability_uptime'],
    labels: { might_uptime: '威能', fury_uptime: '激怒', quickness_uptime: '急速', alacrity_uptime: '敏捷', protection_uptime: '保护', stability_uptime: '稳固' }
  },
  survival: {
    fields: ['damage_taken', 'blocked_count', 'evaded_count', 'dodge_count', 'down_count', 'dead_count', 'downed_damage_taken', 'interrupted_count'],
    labels: { damage_taken: '承伤', blocked_count: '格挡', evaded_count: '闪避', dodge_count: '翻滚', down_count: '倒地', dead_count: '死亡', downed_damage_taken: '倒地承伤', interrupted_count: '被打断' }
  },
  support: {
    fields: ['boon_strips', 'condition_cleanses', 'resurrects', 'condi_cleanse_ally', 'stun_break'],
    labels: { boon_strips: '削增益', condition_cleanses: '清症', resurrects: '复活', condi_cleanse_ally: '队友清症', stun_break: '解控' }
  },
  control: {
    fields: ['downed', 'applied_cc_count', 'applied_cc_duration', 'down_contribution', 'against_downed_damage'],
    labels: { downed: '击倒敌人', applied_cc_count: 'CC次数', applied_cc_duration: 'CC时长', down_contribution: '倒地贡献', against_downed_damage: '对倒地伤害' }
  },
  efficiency: {
    fields: ['wasted', 'saved', 'skill_cast_uptime'],
    labels: { wasted: '技能浪费', saved: '技能节省', skill_cast_uptime: '施法占比' }
  },
  position: {
    fields: ['stack_dist', 'dist_to_com'],
    labels: { stack_dist: '堆叠距离', dist_to_com: '与指挥距离' }
  },
}

/** 数值提取器映射（替代原巨型switch） */
const STAT_VALUE_GETTERS: Record<string, (p: EiAnalysisPlayer) => string> = {
  protection: p => (p.protection_uptime || 0).toFixed(1) + '%',
  protection_uptime: p => (p.protection_uptime || 0).toFixed(1) + '%',
  stability: p => (p.stability_uptime || 0).toFixed(1) + '%',
  stability_uptime: p => (p.stability_uptime || 0).toFixed(1) + '%',
  condition_cleanses: p => fmtCompact(p.condition_cleanses),
  boon_strips: p => fmtCompact(p.boon_strips),
  damage_taken: p => fmtCompact(p.damage_taken),
  hitRate: p => {
    const rate = 100 - ((p.missed || 0) / ((p.missed || 0) + (p.critical_rate || 0) + (p.flanking_rate || 0) + (p.glance_rate || 0) + 1) * 100)
    return rate.toFixed(1) + '%'
  },
  damage: p => fmtCompact(p.damage),
  dps: p => fmtCompact(p.dps),
  power_damage: p => fmtCompact(p.power_damage),
  condi_damage: p => fmtCompact(p.condi_damage),
  breakbar_damage: p => fmtCompact(p.breakbar_damage),
  critical_rate: p => String(p.critical_rate || 0),
  flanking_rate: p => String(p.flanking_rate || 0),
  glance_rate: p => String(p.glance_rate || 0),
  missed: p => String(p.missed || 0),
  interrupts: p => String(p.interrupts || 0),
  might_uptime: p => (p.might_uptime || 0).toFixed(1) + '%',
  fury_uptime: p => (p.fury_uptime || 0).toFixed(1) + '%',
  quickness_uptime: p => (p.quickness_uptime || 0).toFixed(1) + '%',
  alacrity_uptime: p => (p.alacrity_uptime || 0).toFixed(1) + '%',
  blocked_count: p => String(p.blocked_count || 0),
  evaded_count: p => String(p.evaded_count || 0),
  dodge_count: p => String(p.dodge_count || 0),
  down_count: p => String(p.down_count || 0),
  dead_count: p => String(p.dead_count || 0),
  downed_damage_taken: p => fmtCompact(p.downed_damage_taken || 0),
  interrupted_count: p => String(p.interrupted_count || 0),
  resurrects: p => String(p.resurrects || 0),
  condi_cleanse_ally: p => String(p.condi_cleanse_ally || 0),
  stun_break: p => String(p.stun_break || 0),
  downed: p => String(p.downed || 0),
  applied_cc_count: p => String(p.applied_cc_count || 0),
  applied_cc_duration: p => String(p.applied_cc_duration || 0),
  down_contribution: p => String(p.down_contribution || 0),
  against_downed_damage: p => fmtCompact(p.against_downed_damage || 0),
  wasted: p => String(p.wasted || 0),
  saved: p => String(p.saved || 0),
  skill_cast_uptime: p => (p.skill_cast_uptime || 0).toFixed(1) + '%',
  stack_dist: p => (p.stack_dist || 0).toFixed(0),
  dist_to_com: p => (p.dist_to_com || 0).toFixed(0),
}

/** 获取玩家某统计字段的显示值 */
export function getStatValue(p: EiAnalysisPlayer, type: string): string {
  const getter = STAT_VALUE_GETTERS[type]
  return getter ? getter(p) : '-'
}

/** 数值颜色判定映射 */
const HIGH_VALUE_STATS = new Set(['protection', 'protection_uptime', 'stability', 'stability_uptime', 'hitRate', 'skill_cast_uptime'])
const PRIMARY_STATS = new Set(['condition_cleanses', 'boon_strips', 'downed', 'applied_cc_count', 'stun_break'])
const SECONDARY_STATS = new Set(['damage_taken', 'down_count', 'dead_count', 'interrupted_count'])

/** 获取统计值对应的CSS颜色类 */
export function getStatValueClass(type: string, p: EiAnalysisPlayer): string {
  const raw = getStatValue(p, type).replace('%', '')
  const val = parseFloat(raw)
  if (HIGH_VALUE_STATS.has(type)) {
    return val >= 70 ? 'text-success' : val >= 40 ? 'text-warning' : 'text-error'
  }
  if (PRIMARY_STATS.has(type)) return 'text-primary'
  if (SECONDARY_STATS.has(type)) return 'text-secondary'
  return 'text-neutral-text'
}

// 以下函数已废弃，数据计算已迁移至后端
// export function calcHitRate(p: EiAnalysisPlayer): number
// export function getTeamTotalDamage(g: { players: EiAnalysisPlayer[] }): number
// export function getTeamAvgDps(g: { players: EiAnalysisPlayer[] }): number
// export function getTeamAvgScore(g: { players: EiAnalysisPlayer[] }): number | undefined
// export function getTeamDownedCount(g: { players: EiAnalysisPlayer[] }): number
// export function getTeamDeathCount(g: { players: EiAnalysisPlayer[] }): number
