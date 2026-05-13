import { computed, ref } from 'vue'
import { useDictMapping } from '@/composables/core/useDictMapping'

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

export interface FlatEvent extends RotationEvent {
  state: 'full' | 'interrupted' | 'instant' | 'unknown'
}

export interface SimpleCycle {
  events: FlatEvent[]
  duration: number
}

export interface AdvancedCast {
  castTime: number
  duration: number
  state: FlatEvent['state']
  left: number
  width: number
}

export interface AdvancedSkillRow {
  skillId: number | string
  name: string
  icon?: string
  casts: AdvancedCast[]
}

export interface TimeTick {
  time: number
  position: number
}

export function getStateLabel(state: string): string {
  // 从字典表获取状态标签（若字典未加载则返回原始值）
  const { getLabel } = useDictMapping('skill_state', false)
  return getLabel(state) || state
}

function getEventState(evt: RotationEvent): FlatEvent['state'] {
  if (evt.isSwap) return 'full'
  if (evt.isInstant || evt.duration === 0) return 'instant'
  if (evt.timeGained < -30 || evt.duration < 150) return 'interrupted'
  if (evt.duration > 0) return 'full'
  return 'unknown'
}

export function useSkillRotationTimeline(props: { events: RotationEvent[]; fightDuration?: number }) {
  const viewMode = ref<'simple' | 'advanced'>('simple')
  const showAutoAttacks = ref(true)
  const showInstantCast = ref(true)
  const hoveredEvent = ref<FlatEvent | AdvancedCast | null>(null)
  const advancedTrackRef = ref<HTMLDivElement | null>(null)
  const advancedScrollLeft = ref(0)

  const flatEvents = computed<FlatEvent[]>(() => {
    const events = [...props.events].sort((a, b) => a.castTime - b.castTime)
    return events.map(evt => ({ ...evt, state: getEventState(evt) }))
  })

  const simpleCycles = computed<SimpleCycle[]>(() => {
    const events = flatEvents.value
    if (events.length === 0) return []
    const cycles: SimpleCycle[] = []
    let current: FlatEvent[] = []
    for (const evt of events) {
      if (evt.isSwap && current.length > 0) {
        current.push(evt)
        cycles.push({ events: [...current], duration: current[current.length - 1].castTime - current[0].castTime })
        current = []
      } else {
        current.push(evt)
      }
    }
    if (current.length > 0) {
      cycles.push({ events: current, duration: current[current.length - 1].castTime - current[0].castTime })
    }
    return cycles.map(cycle => ({
      ...cycle,
      events: cycle.events.filter(evt => {
        if (!showAutoAttacks.value && evt.autoAttack) return false
        if (!showInstantCast.value && evt.state === 'instant' && !evt.isSwap) return false
        return true
      })
    })).filter(cycle => cycle.events.length > 0)
  })

  const advancedSkillRows = computed<AdvancedSkillRow[]>(() => {
    const events = flatEvents.value
    if (events.length === 0) return []
    const durationMs = (props.fightDuration || 1) * 1000
    if (durationMs <= 0) return []
    const skillMap = new Map<string, AdvancedSkillRow>()
    for (const evt of events) {
      const sid = String(evt.skillId)
      if (!skillMap.has(sid)) {
        skillMap.set(sid, { skillId: evt.skillId, name: evt.name, icon: evt.icon, casts: [] })
      }
      const row = skillMap.get(sid)!
      const left = (evt.castTime / durationMs) * 100
      const width = Math.max((evt.duration / durationMs) * 100, 0.3)
      row.casts.push({ castTime: evt.castTime, duration: evt.duration, state: evt.state, left, width: Math.min(width, 100 - left) })
    }
    return Array.from(skillMap.values()).sort((a, b) => b.casts.length - a.casts.length)
  })

  const advancedTimeTicks = computed<TimeTick[]>(() => {
    const duration = props.fightDuration || 0
    if (duration <= 0) return []
    let interval = 5
    if (duration > 300) interval = 30
    else if (duration > 120) interval = 15
    else if (duration > 60) interval = 10
    const ticks: TimeTick[] = []
    for (let t = 0; t <= duration; t += interval) {
      ticks.push({ time: t, position: (t / duration) * 100 })
    }
    return ticks
  })

  const advancedContentStyle = computed(() => ({ minWidth: '800px' }))

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    const ms = Math.floor((seconds % 1) * 100)
    if (m > 0) return `${m}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`
    return `${s}.${ms.toString().padStart(2, '0')}s`
  }

  function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    if (m > 0) return `${m}分${s}秒`
    return `${s}秒`
  }

  function handleAdvancedScroll() {
    if (advancedTrackRef.value) advancedScrollLeft.value = advancedTrackRef.value.scrollLeft
  }

  return {
    viewMode, showAutoAttacks, showInstantCast, hoveredEvent,
    advancedTrackRef, advancedScrollLeft, advancedContentStyle,
    flatEvents, simpleCycles, advancedSkillRows, advancedTimeTicks,
    formatTime, formatDuration, handleAdvancedScroll
  }
}
