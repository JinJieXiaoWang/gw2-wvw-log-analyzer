/**
 * 技能循环分析工具函数与常量
 * 纯函数、无副作用
 */

import type { RotationEvent, CycleEvent, HeatmapRow } from './rotationTypes'

/** 状态标签常量（UI 级别，非业务常量） */
export const STATE_LABELS: Record<string, string> = {
  full: '完整施放',
  interrupted: '被打断',
  instant: '瞬发',
  swap: '武器切换',
  trait: '特性触发',
}

/** 视图模式标签常量（UI 级别，非业务常量） */
export const VIEW_LABELS = {
  cycle: '循环视图',
  timeline: '时间轴',
  heatmap: '热力图',
}

/** 过滤选项标签常量（UI 级别，非业务常量） */
export const FILTER_LABELS = {
  showAuto: '普攻',
  showInstant: '瞬发',
  showSwap: '武器切换',
  showTrait: '特性触发',
}

/** 热力图颜色常量 */
const HEATMAP_COLORS = [
  'rgba(148, 163, 184, 0.1)',
  'rgba(34, 211, 238, 0.25)',
  'rgba(34, 211, 238, 0.5)',
  'rgba(34, 211, 238, 0.75)',
  'rgba(34, 211, 238, 1)',
]

/** 获取事件状态 */
export function getEventState(evt: RotationEvent): CycleEvent['state'] {
  if (evt.isSwap) return 'swap'
  if (evt.isTraitProc) return 'trait'
  if (evt.isInstant || evt.duration === 0) return 'instant'
  if (evt.timeGained < -30 || evt.duration < 150) return 'interrupted'
  return 'full'
}

/** 获取热力图颜色 */
export function getHeatmapColor(count: number): string {
  if (count === 0) return HEATMAP_COLORS[0]
  if (count <= 2) return HEATMAP_COLORS[1]
  if (count <= 5) return HEATMAP_COLORS[2]
  if (count <= 10) return HEATMAP_COLORS[3]
  return HEATMAP_COLORS[4]
}

/** 格式化时间（毫秒 -> M:SS.ms 或 S.ms） */
export function formatTime(ms: number): string {
  const seconds = ms / 1000
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  const msPart = Math.floor((seconds % 1) * 100)
  if (m > 0) return `${m}:${s.toString().padStart(2, '0')}.${msPart.toString().padStart(2, '0')}`
  return `${s}.${msPart.toString().padStart(2, '0')}s`
}

/** 格式化战斗时长（秒 -> X分X秒） */
export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  if (m > 0) return `${m}分${s}秒`
  return `${s}秒`
}

/** 格式化循环时长（毫秒 -> X秒 或 X分X秒） */
export function formatCycleTime(ms: number): string {
  const seconds = ms / 1000
  if (seconds < 60) return `${Math.round(seconds)}秒`
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}分${s}秒`
}

/** 默认过滤选项 */
export function getDefaultFilters() {
  return {
    showAuto: false,
    showInstant: true,
    showSwap: true,
    showTrait: false,
  }
}

/** 计算过滤后的事件 */
export function computeFilteredEvents(events: RotationEvent[], filters: { showAuto: boolean; showInstant: boolean; showSwap: boolean; showTrait: boolean }): CycleEvent[] {
  return events
    .map(evt => ({ ...evt, state: getEventState(evt) }))
    .filter(evt => {
      if (!filters.showAuto && evt.autoAttack) return false
      if (!filters.showInstant && evt.isInstant && !evt.isSwap) return false
      if (!filters.showSwap && evt.isSwap) return false
      if (!filters.showTrait && evt.isTraitProc) return false
      return true
    })
    .sort((a, b) => a.castTime - b.castTime)
}

/** 计算循环数据 */
export function computeCycles(events: CycleEvent[]): import('./rotationTypes').SkillCycle[] {
  if (events.length === 0) return []
  const cycles: import('./rotationTypes').SkillCycle[] = []
  let current: CycleEvent[] = []
  for (const evt of events) {
    if (evt.isSwap && current.length > 0) {
      current.push(evt)
      cycles.push({
        events: [...current],
        duration: current[current.length - 1].castTime - current[0].castTime,
        interruptedCount: current.filter(e => e.state === 'interrupted').length,
      })
      current = []
    } else {
      current.push(evt)
    }
  }
  if (current.length > 0) {
    cycles.push({
      events: current,
      duration: current.length > 1 ? current[current.length - 1].castTime - current[0].castTime : 0,
      interruptedCount: current.filter(e => e.state === 'interrupted').length,
    })
  }
  return cycles
}

/** 计算时间轴刻度 */
export function computeTimelineTicks(fightDuration: number): import('./rotationTypes').TimelineTick[] {
  const duration = fightDuration || 60
  const interval = duration > 120 ? 10 : duration > 60 ? 5 : 2
  const ticks: import('./rotationTypes').TimelineTick[] = []
  for (let t = 0; t <= duration; t += interval) {
    ticks.push({ time: t, position: (t / duration) * 100 })
  }
  return ticks
}

/** 计算技能轨道 */
export function computeSkillTracks(events: CycleEvent[], fightDuration: number): import('./rotationTypes').SkillTrack[] {
  const durationMs = (fightDuration || 1) * 1000
  const skillMap = new Map<string, import('./rotationTypes').SkillTrack>()
  for (const evt of events) {
    const sid = String(evt.skillId)
    if (!skillMap.has(sid)) {
      skillMap.set(sid, { skillId: evt.skillId, name: evt.name, icon: evt.icon, casts: [] })
    }
    const track = skillMap.get(sid)!
    const position = (evt.castTime / durationMs) * 100
    const width = Math.max((evt.duration / durationMs) * 100, 0.5)
    track.casts.push({
      castTime: evt.castTime,
      duration: evt.duration,
      state: evt.state,
      position,
      width: Math.min(width, 100 - position),
      skillId: evt.skillId,
      timeGained: evt.timeGained,
      quickness: evt.quickness,
      name: evt.name,
      icon: evt.icon,
    })
  }
  return Array.from(skillMap.values()).sort((a, b) => b.casts.length - a.casts.length)
}

/** 计算热力图数据 */
export function computeHeatmap(events: CycleEvent[], fightDuration: number): HeatmapRow[] {
  if (events.length === 0) return []
  const duration = fightDuration || 60
  const bucketSize = 5
  const buckets = Math.ceil(duration / bucketSize)
  const skillMap = new Map<string, number[]>()
  const skillNames = new Map<string, string>()
  for (const evt of events) {
    const sid = String(evt.skillId)
    if (!skillMap.has(sid)) {
      skillMap.set(sid, new Array(buckets).fill(0))
      skillNames.set(sid, evt.name)
    }
    const bucket = Math.min(Math.floor(evt.castTime / 1000 / bucketSize), buckets - 1)
    skillMap.get(sid)![bucket]++
  }
  return Array.from(skillMap.entries())
    .map(([id, counts]) => ({ label: skillNames.get(id) || id, cells: counts.map(count => ({ count })) }))
    .sort((a, b) => {
      const sumA = a.cells.reduce((s, c) => s + c.count, 0)
      const sumB = b.cells.reduce((s, c) => s + c.count, 0)
      return sumB - sumA
    })
    .slice(0, 15)
}

/** 生成时序图数据（简化接口） */
export function generateTimelineData(events: any[], fightDuration: number) {
  const filtered = events.map((evt: any) => ({
    ...evt,
    castTime: (evt.time || 0) * 1000,
    state: evt.state || 'full',
    timeGained: 0,
    quickness: false,
  }))
  const ticks = computeTimelineTicks(fightDuration)
  const tracks = computeSkillTracks(filtered, fightDuration)
  return { ticks, tracks }
}

/** 生成热力图数据（简化接口） */
export function generateHeatmapData(skillCasts: any[], events: any[]) {
  const filtered = events.map((evt: any) => ({
    ...evt,
    castTime: (evt.time || 0) * 1000,
    state: evt.state || 'full',
    timeGained: 0,
    quickness: false,
  }))
  return computeHeatmap(filtered, 120)
}

/** 生成循环数据（简化接口） */
export function generateCycleData(events: any[]): import('./rotationTypes').SkillCycle[] {
  const filtered = events.map((evt: any) => ({
    ...evt,
    castTime: (evt.time || 0) * 1000,
    state: evt.state || 'full',
    timeGained: 0,
    quickness: false,
    isSwap: evt.isSwap || false,
  }))
  return computeCycles(filtered)
}
