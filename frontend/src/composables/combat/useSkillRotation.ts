/**
 * useSkillRotation - 技能循环分析业务逻辑 composable
 */

import { ref, computed, reactive } from 'vue'
import type { RotationEvent, CycleEvent, SkillCycle, TimelineTick, SkillTrack, HeatmapRow, FilterOptions } from '@/utils/combat/rotationTypes'
import {
  getDefaultFilters,
  computeFilteredEvents,
  computeCycles,
  computeTimelineTicks,
  computeSkillTracks,
  computeHeatmap,
} from '@/utils/combat/rotation'

export function useSkillRotation(events: RotationEvent[], fightDuration?: number) {
  const viewMode = ref<'cycle' | 'timeline' | 'heatmap'>('cycle')
  const hoveredSkill = ref<CycleEvent | null>(null)
  const tooltipPosition = reactive({ x: 0, y: 0 })
  const filterOptions = reactive<FilterOptions>(getDefaultFilters())

  const filteredEvents = computed<CycleEvent[]>(() => computeFilteredEvents(events, filterOptions))

  const filteredCycles = computed<SkillCycle[]>(() => computeCycles(filteredEvents.value))

  const timelineTicks = computed<TimelineTick[]>(() => computeTimelineTicks(fightDuration || 0))

  const skillTracks = computed<SkillTrack[]>(() => computeSkillTracks(filteredEvents.value, fightDuration || 0))

  const heatmapData = computed<HeatmapRow[]>(() => computeHeatmap(filteredEvents.value, fightDuration || 0))

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
  }
}
