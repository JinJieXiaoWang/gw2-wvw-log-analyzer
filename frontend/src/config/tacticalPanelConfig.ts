/**
 * 战术分析面板配置
 * 功能：集中管理所有可配置的展示参数，消除硬编码魔法数字
 */

/** 图层样式配置 - 使用Tailwind类名 */
export const TACTICAL_LAYER_STYLES: Record<string, {
  icon: string
  labelKey: string
  iconColorClass: string
  gradientClass: string
  borderClass: string
}> = {
  team: {
    icon: 'pi pi-users',
    labelKey: 'tactical.layers.team',
    iconColorClass: 'text-info',
    gradientClass: 'bg-gradient-to-br from-info/10 to-blue-500/10',
    borderClass: 'border-info/20',
  },
  damage: {
    icon: 'pi pi-chart-line',
    labelKey: 'tactical.layers.damage',
    iconColorClass: 'text-primary',
    gradientClass: 'bg-gradient-to-br from-primary/10 to-purple-500/10',
    borderClass: 'border-primary/20',
  },
  buff: {
    icon: 'pi pi-shield',
    labelKey: 'tactical.layers.buff',
    iconColorClass: 'text-warning',
    gradientClass: 'bg-gradient-to-br from-warning/10 to-amber-500/10',
    borderClass: 'border-warning/20',
  },
  survival: {
    icon: 'pi pi-heart',
    labelKey: 'tactical.layers.survival',
    iconColorClass: 'text-status-success',
    gradientClass: 'bg-gradient-to-br from-status-success/10 to-emerald-500/10',
    borderClass: 'border-status-success/20',
  },
} as const

/** 展示数量限制配置 */
export const TACTICAL_DISPLAY_LIMITS = {
  /** DPS排行榜显示人数 */
  topDpsCount: 3,
  /** Buff/Defense leaders显示人数 */
  maxLeadersDisplay: 2,
  /** Buff网格最小列数 */
  buffGridMinCols: 2,
  /** Buff网格最大列数 */
  buffGridMaxCols: 4,
} as const

/** 字段标签回退映射 */
export const TACTICAL_LABEL_MAP: Record<string, string> = {
  might: 'tactical.labels.might',
  fury: 'tactical.labels.fury',
  quickness: 'tactical.labels.quickness',
  alacrity: 'tactical.labels.alacrity',
  stability: 'tactical.labels.stability',
  protection: 'tactical.labels.protection',
  boon_strips: 'tactical.labels.boonStrip',
  condition_cleanses: 'tactical.labels.condiCleanse',
  resurrects: 'tactical.labels.resurrect',
  damage_taken: 'tactical.labels.damageTaken',
  dodge_count: 'tactical.labels.dodgeCount',
}
