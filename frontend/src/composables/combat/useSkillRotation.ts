/**
 * useSkillRotation - 技能循环分析业务逻辑 composable
 * 支持 cycle / timeline / heatmap / simple / advanced 视图
 */

import { ref, computed, reactive } from 'vue'
import type {
  RotationEvent,
  CycleEvent,
  SkillCycle,
  TimelineTick,
  SkillTrack,
  HeatmapRow,
  FilterOptions,
  FlatEvent,
  SimpleCycle,
  AdvancedSkillRow,
  AdvancedCast,
  TimeTick,
} from '@/utils/combat/rotationTypes'
import {
  getDefaultFilters,
  computeFilteredEvents,
  computeCycles,
  computeTimelineTicks,
  computeSkillTracks,
  computeHeatmap,
  computeSimpleCycles,
  computeAdvancedSkillRows,
  computeAdvancedTimeTicks,
} from '@/utils/combat/rotation'

export function useSkillRotation(events: RotationEvent[], fightDuration?: number) {
  const viewMode = ref<'cycle' | 'timeline' | 'heatmap' | 'simple' | 'advanced'>('cycle')
  const hoveredSkill = ref<CycleEvent | null>(null)
  const tooltipPosition = reactive({ x: 0, y: 0 })
  const filterOptions = reactive<FilterOptions>(getDefaultFilters())

  // simple / advanced 视图特有状态
  const showAutoAttacks = ref(true)
  const showInstantCast = ref(true)
  const hoveredEvent = ref<FlatEvent | AdvancedCast | null>(null)
  const advancedTrackRef = ref<HTMLDivElement | null>(null)
  const advancedScrollLeft = ref(0)

  const filteredEvents = computed<CycleEvent[]>(() => computeFilteredEvents(events, filterOptions))

  const filteredCycles = computed<SkillCycle[]>(() => computeCycles(filteredEvents.value))

  const timelineTicks = computed<TimelineTick[]>(() => computeTimelineTicks(fightDuration || 0))

  const skillTracks = computed<SkillTrack[]>(() => computeSkillTracks(filteredEvents.value, fightDuration || 0))

  const heatmapData = computed<HeatmapRow[]>(() => computeHeatmap(filteredEvents.value, fightDuration || 0))

  const simpleCycles = computed<SimpleCycle[]>(() =>
    computeSimpleCycles(events, { showAutoAttacks: showAutoAttacks.value, showInstantCast: showInstantCast.value })
  )

  const advancedSkillRows = computed<AdvancedSkillRow[]>(() =>
    computeAdvancedSkillRows(events, fightDuration || 0)
  )

  const advancedTimeTicks = computed<TimeTick[]>(() =>
    computeAdvancedTimeTicks(fightDuration || 0)
  )

  const advancedContentStyle = computed(() => ({ minWidth: '800px' }))

  const tooltipStyle = computed(() => ({
    left: `${tooltipPosition.x}px`,
    top: `${tooltipPosition.y}px`,
  }))

  function handleMouseMove(event: MouseEvent) {
    tooltipPosition.x = event.clientX + 16
    tooltipPosition.y = event.clientY + 16
  }

  function resetFilters() {
    const defaults = getDefaultFilters()
    filterOptions.showAuto = defaults.showAuto
    filterOptions.showInstant = defaults.showInstant
    filterOptions.showSwap = defaults.showSwap
    filterOptions.showTrait = defaults.showTrait
  }

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
    if (advancedTrackRef.value) {
      advancedScrollLeft.value = advancedTrackRef.value.scrollLeft
    }
  }

  return {
    viewMode,
    hoveredSkill,
    tooltipPosition,
    tooltipStyle,
    filterOptions,
    filteredEvents,
    filteredCycles,
    timelineTicks,
    skillTracks,
    heatmapData,
    handleMouseMove,
    resetFilters,
    // simple / advanced
    showAutoAttacks,
    showInstantCast,
    hoveredEvent,
    advancedTrackRef,
    advancedScrollLeft,
    advancedContentStyle,
    simpleCycles,
    advancedSkillRows,
    advancedTimeTicks,
    formatTime,
    formatDuration,
    handleAdvancedScroll,
  }
}
