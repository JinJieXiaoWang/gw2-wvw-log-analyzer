/**
 * 技能循环分析相关类型定义
 */

export interface RotationEvent {
  castTime: number
  skillId: number | string
  duration: number
  timeGained: number
  quickness: number
  name: string
  icon?: string
  autoAttack?: boolean
  isSwap?: boolean
  isInstant?: boolean
  isTraitProc?: boolean
  gw2Id?: number
}

export interface CycleEvent extends RotationEvent {
  state: 'full' | 'interrupted' | 'instant' | 'swap' | 'trait'
}

export interface SkillCycle {
  events: CycleEvent[]
  duration: number
  interruptedCount: number
}

export interface TimelineTick {
  time: number
  position: number
}

export interface TrackCast {
  castTime: number
  duration: number
  state: CycleEvent['state']
  position: number
  width: number
  skillId: number | string
  timeGained: number
  quickness: number
  name: string
  icon?: string
}

export interface SkillTrack {
  skillId: number | string
  name: string
  icon?: string
  casts: TrackCast[]
}

export interface HeatmapCell {
  count: number
}

export interface HeatmapRow {
  label: string
  cells: HeatmapCell[]
}

export interface FilterOptions {
  showAuto: boolean
  showInstant: boolean
  showSwap: boolean
  showTrait: boolean
}
