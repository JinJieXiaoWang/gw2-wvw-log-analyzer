import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import type { ComputedRef, Ref } from 'vue'
import { computed } from 'vue'

export type StatCategory =
  | 'protection' | 'stability' | 'condition_cleanses' | 'boon_strips' | 'damage_taken' | 'hitRate'
  | 'damage_output' | 'hit_quality' | 'buff_coverage' | 'survival' | 'support' | 'control' | 'efficiency' | 'position'

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

export const getStatValue = (p: EiAnalysisPlayer, type: string) => {
  switch (type) {
    case 'protection':
    case 'protection_uptime': return (p.protection_uptime || 0).toFixed(1) + '%'
    case 'stability':
    case 'stability_uptime': return (p.stability_uptime || 0).toFixed(1) + '%'
    case 'condition_cleanses': return fmtCompact(p.condition_cleanses)
    case 'boon_strips': return fmtCompact(p.boon_strips)
    case 'damage_taken': return fmtCompact(p.damage_taken)
    case 'hitRate': {
      const rate = 100 - ((p.missed || 0) / ((p.missed || 0) + (p.critical_rate || 0) + (p.flanking_rate || 0) + (p.glance_rate || 0) + 1) * 100)
      return rate.toFixed(1) + '%'
    }
    case 'damage': return fmtCompact(p.damage)
    case 'dps': return fmtCompact(p.dps)
    case 'power_damage': return fmtCompact(p.power_damage)
    case 'condi_damage': return fmtCompact(p.condi_damage)
    case 'breakbar_damage': return fmtCompact(p.breakbar_damage)
    case 'critical_rate': return String(p.critical_rate || 0)
    case 'flanking_rate': return String(p.flanking_rate || 0)
    case 'glance_rate': return String(p.glance_rate || 0)
    case 'missed': return String(p.missed || 0)
    case 'interrupts': return String(p.interrupts || 0)
    case 'might_uptime': return (p.might_uptime || 0).toFixed(1) + '%'
    case 'fury_uptime': return (p.fury_uptime || 0).toFixed(1) + '%'
    case 'quickness_uptime': return (p.quickness_uptime || 0).toFixed(1) + '%'
    case 'alacrity_uptime': return (p.alacrity_uptime || 0).toFixed(1) + '%'
    case 'blocked_count': return String(p.blocked_count || 0)
    case 'evaded_count': return String(p.evaded_count || 0)
    case 'dodge_count': return String(p.dodge_count || 0)
    case 'down_count': return String(p.down_count || 0)
    case 'dead_count': return String(p.dead_count || 0)
    case 'downed_damage_taken': return fmtCompact(p.downed_damage_taken || 0)
    case 'interrupted_count': return String(p.interrupted_count || 0)
    case 'resurrects': return String(p.resurrects || 0)
    case 'condi_cleanse_ally': return String(p.condi_cleanse_ally || 0)
    case 'stun_break': return String(p.stun_break || 0)
    case 'downed': return String(p.downed || 0)
    case 'applied_cc_count': return String(p.applied_cc_count || 0)
    case 'applied_cc_duration': return String(p.applied_cc_duration || 0)
    case 'down_contribution': return String(p.down_contribution || 0)
    case 'against_downed_damage': return fmtCompact(p.against_downed_damage || 0)
    case 'wasted': return String(p.wasted || 0)
    case 'saved': return String(p.saved || 0)
    case 'skill_cast_uptime': return (p.skill_cast_uptime || 0).toFixed(1) + '%'
    case 'stack_dist': return (p.stack_dist || 0).toFixed(0)
    case 'dist_to_com': return (p.dist_to_com || 0).toFixed(0)
    default: return '-'
  }
}

export const getStatValueClass = (type: string, p: EiAnalysisPlayer) => {
  const val = parseFloat(getStatValue(p, type).replace('%', ''))
  switch (type) {
    case 'protection':
    case 'protection_uptime':
    case 'stability':
    case 'stability_uptime':
    case 'hitRate':
    case 'skill_cast_uptime':
      return val >= 70 ? 'text-success' : val >= 40 ? 'text-warning' : 'text-error'
    case 'condition_cleanses':
    case 'boon_strips':
    case 'downed':
    case 'applied_cc_count':
    case 'stun_break':
      return 'text-primary'
    case 'damage_taken':
    case 'down_count':
    case 'dead_count':
    case 'interrupted_count':
      return 'text-secondary'
    default:
      return 'text-neutral-text'
  }
}

export function useStatDetail(
  players: ComputedRef<EiAnalysisPlayer[]>,
  currentStatType: Ref<StatCategory>,
  currentStatCategory: Ref<string[]>
) {
  const statDetailList = computed(() => {
    const list = [...players.value]
    const type = currentStatType.value
    const sortKey = CATEGORY_SORT_KEY[type] || 'damage'
    if (type === 'hitRate') {
      return list.sort((a, b) => {
        const aRate = 100 - ((a.missed || 0) / ((a.missed || 0) + (a.critical_rate || 0) + (a.flanking_rate || 0) + (a.glance_rate || 0) + 1) * 100)
        const bRate = 100 - ((b.missed || 0) / ((b.missed || 0) + (b.critical_rate || 0) + (b.flanking_rate || 0) + (b.glance_rate || 0) + 1) * 100)
        return bRate - aRate
      })
    }
    return list.sort((a: any, b: any) => (b[sortKey] || 0) - (a[sortKey] || 0))
  })

  const statDetailAverage = computed(() => {
    const fields = currentStatCategory.value
    const list = statDetailList.value
    if (!list.length || !fields.length) return 0
    let total = 0
    let count = 0
    for (const p of list) {
      for (const f of fields) {
        const val = getStatValue(p, f)
        const num = parseFloat(String(val).replace('%', '').replace(/,/g, ''))
        if (!isNaN(num) && isFinite(num)) {
          total += num
          count++
        }
      }
    }
    return count > 0 ? total / count : 0
  })

  return { statDetailList, statDetailAverage }
}
