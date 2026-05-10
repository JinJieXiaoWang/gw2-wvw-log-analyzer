<template>
  <div class="skill-rotation-viewer">
    <!-- Header -->
    <div class="sr-header">
      <div class="sr-title-section">
        <div class="sr-icon-wrapper"><i class="pi pi-clock" /></div>
        <div>
          <h3 class="sr-title">技能循环分析</h3>
          <p class="sr-subtitle">ս斗时长: {{ formatDuration(props.fightDuration || 0) }} | 技能总数: {{ props.events.length }}</p>
        </div>
      </div>
      <div class="sr-view-toggle">
        <button v-for="mode in viewModes" :key="mode.key" type="button" class="toggle-btn" :class="{ active: viewMode === mode.key }" @click="viewMode = mode.key">
          <i :class="mode.icon" /><span>{{ mode.label }}</span>
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="sr-filters">
      <div class="filter-group">
        <label v-for="opt in filterOpts" :key="opt.key" class="filter-checkbox">
          <input v-model="filterOptions[opt.key as keyof FilterOptions]" type="checkbox">
          <span class="filter-icon">{{ opt.icon }}</span>
          <span>{{ opt.label }}</span>
        </label>
      </div>
      <div class="filter-actions">
        <button type="button" class="btn-icon" @click="resetFilters"><i class="pi pi-refresh" /></button>
      </div>
    </div>

    <!-- Views -->
    <RotationCycleView v-if="viewMode === 'cycle'" :cycles="filteredCycles" @hover-skill="hoveredSkill = $event" @leave-skill="hoveredSkill = null" @mousemove="handleMouseMove" />
    <RotationTimelineView v-else-if="viewMode === 'timeline'" :ticks="timelineTicks" :tracks="skillTracks" @hover-skill="hoveredSkill = $event" @leave-skill="hoveredSkill = null" @mousemove="handleMouseMove" />
    <RotationHeatmapView v-else :rows="heatmapData" />

    <!-- Tooltip -->
    <Transition name="tooltip">
      <div v-if="hoveredSkill" class="sr-tooltip" :style="tooltipStyle">
        <div class="tooltip-header">
          <img v-if="hoveredSkill.icon" :src="hoveredSkill.icon" class="tooltip-icon">
          <div class="tooltip-title-section">
            <span class="tooltip-title">{{ hoveredSkill.name }}</span>
            <span class="tooltip-state" :class="`state-${hoveredSkill.state}`">{{ STATE_LABELS[hoveredSkill.state] }}</span>
          </div>
        </div>
        <div class="tooltip-body">
          <div class="tooltip-row"><span class="tooltip-label">ʩ放时间</span><span class="tooltip-value">{{ formatTime(hoveredSkill.castTime) }}</span></div>
          <div class="tooltip-row"><span class="tooltip-label">持续时间</span><span class="tooltip-value">{{ hoveredSkill.duration }}ms</span></div>
          <div v-if="hoveredSkill.timeGained !== 0" class="tooltip-row">
            <span class="tooltip-label">动画差</span>
            <span class="tooltip-value" :class="hoveredSkill.timeGained < 0 ? 'negative' : ''">{{ hoveredSkill.timeGained > 0 ? '+' : '' }}{{ hoveredSkill.timeGained }}ms</span>
          </div>
          <div class="tooltip-row"><span class="tooltip-label">急速</span><span class="tooltip-value">{{ Math.round((hoveredSkill.quickness || 0) * 100) }}%</span></div>
        </div>
      </div>
    </Transition>

    <!-- Legend -->
    <div class="sr-legend">
      <div class="legend-title">״̬˵明</div>
      <div class="legend-items">
        <div v-for="s in legendItems" :key="s.key" class="legend-item">
          <span class="legend-color" :class="s.key" />
          <span class="legend-text">{{ s.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSkillRotation } from '@/composables/combat/useSkillRotation'
import { formatTime, formatDuration, STATE_LABELS, VIEW_LABELS, FILTER_LABELS } from '@/utils/combat/rotation'
import type { RotationEvent, FilterOptions } from '@/utils/combat/rotationTypes'
import RotationCycleView from './rotation/RotationCycleView.vue'
import RotationTimelineView from './rotation/RotationTimelineView.vue'
import RotationHeatmapView from './rotation/RotationHeatmapView.vue'

const props = defineProps<{
  events: RotationEvent[]
  fightDuration?: number
}>()

const {
  viewMode, hoveredSkill, tooltipStyle, filterOptions,
  filteredCycles, timelineTicks, skillTracks, heatmapData,
  handleMouseMove, resetFilters,
} = useSkillRotation(props.events, props.fightDuration)

const viewModes = computed(() => [
  { key: 'cycle' as const, icon: 'pi pi-repeat', label: VIEW_LABELS.cycle },
  { key: 'timeline' as const, icon: 'pi pi-bar-chart', label: VIEW_LABELS.timeline },
  { key: 'heatmap' as const, icon: 'pi pi-calendar', label: VIEW_LABELS.heatmap },
])

const filterOpts = computed(() => [
  { key: 'showAuto' as const, icon: '⚔️', label: FILTER_LABELS.showAuto },
  { key: 'showInstant' as const, icon: '⚡', label: FILTER_LABELS.showInstant },
  { key: 'showSwap' as const, icon: '🔄', label: FILTER_LABELS.showSwap },
  { key: 'showTrait' as const, icon: '✨', label: FILTER_LABELS.showTrait },
])

const legendItems = computed(() => [
  { key: 'full', label: STATE_LABELS.full },
  { key: 'interrupted', label: STATE_LABELS.interrupted },
  { key: 'instant', label: STATE_LABELS.instant },
  { key: 'swap', label: STATE_LABELS.swap },
  { key: 'trait', label: STATE_LABELS.trait },
])
</script>

<style scoped>
.skill-rotation-viewer { display: flex; flex-direction: column; gap: 1rem; width: 100%; padding: 1rem; background: var(--color-bg-secondary, #0f172a); border-radius: 0.75rem; border: 1px solid var(--color-border, rgba(255,255,255,0.08)); }
.sr-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--color-border, rgba(255,255,255,0.08)); }
.sr-title-section { display: flex; align-items: center; gap: 0.75rem; }
.sr-icon-wrapper { width: 40px; height: 40px; border-radius: 0.5rem; background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2)); display: flex; align-items: center; justify-content: center; color: #60a5fa; font-size: 1.125rem; }
.sr-title { margin: 0; font-size: 1.125rem; font-weight: 700; color: var(--color-text-primary, #f1f5f9); }
.sr-subtitle { margin: 0.25rem 0 0; font-size: 0.75rem; color: var(--color-text-secondary, #94a3b8); }
.sr-view-toggle { display: flex; gap: 0.25rem; background: rgba(255,255,255,0.04); border-radius: 0.375rem; padding: 0.25rem; }
.toggle-btn { display: flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; border: none; border-radius: 0.25rem; background: transparent; color: var(--color-text-secondary, #94a3b8); font-size: 0.75rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; }
.toggle-btn:hover { color: var(--color-text-primary, #f1f5f9); background: rgba(255,255,255,0.05); }
.toggle-btn.active { background: var(--color-primary, #3b82f6); color: white; }
.sr-filters { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; }
.filter-group { display: flex; gap: 1rem; }
.filter-checkbox { display: flex; align-items: center; gap: 0.375rem; cursor: pointer; font-size: 0.7rem; color: var(--color-text-secondary, #94a3b8); transition: color 0.15s; }
.filter-checkbox:hover { color: var(--color-text-primary, #f1f5f9); }
.filter-checkbox input { accent-color: var(--color-primary, #3b82f6); }
.filter-icon { font-size: 0.75rem; }
.filter-actions { display: flex; gap: 0.25rem; }
.btn-icon { padding: 0.375rem; border: none; border-radius: 0.25rem; background: rgba(255,255,255,0.04); color: var(--color-text-secondary, #94a3b8); cursor: pointer; transition: all 0.15s; }
.btn-icon:hover { background: rgba(255,255,255,0.08); color: var(--color-text-primary, #f1f5f9); }
.sr-tooltip { position: fixed; background: rgba(15,23,42,0.98); border: 1px solid rgba(255,255,255,0.1); border-radius: 0.5rem; padding: 0.625rem; min-width: 200px; z-index: 1000; box-shadow: 0 12px 32px rgba(0,0,0,0.4); pointer-events: none; transform: translate(-50%, -100%) translateY(-8px); }
.tooltip-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.08); }
.tooltip-icon { width: 32px; height: 32px; border-radius: 0.375rem; }
.tooltip-title-section { display: flex; flex-direction: column; gap: 0.125rem; }
.tooltip-title { font-size: 0.875rem; font-weight: 700; color: #f1f5f9; }
.tooltip-state { font-size: 0.65rem; padding: 0.125rem 0.375rem; border-radius: 0.25rem; }
.tooltip-state.state-full { background: rgba(34,211,238,0.15); color: #22d3ee; }
.tooltip-state.state-interrupted { background: rgba(239,68,68,0.15); color: #ef4444; }
.tooltip-state.state-instant { background: rgba(59,130,246,0.15); color: #3b82f6; }
.tooltip-body { display: flex; flex-direction: column; gap: 0.25rem; }
.tooltip-row { display: flex; justify-content: space-between; }
.tooltip-label { font-size: 0.7rem; color: var(--color-text-secondary, #94a3b8); }
.tooltip-value { font-size: 0.7rem; color: #f1f5f9; font-weight: 500; }
.tooltip-value.negative { color: #ef4444; }
.sr-legend { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; padding: 0.5rem; background: rgba(255,255,255,0.02); border-radius: 0.375rem; }
.legend-title { font-size: 0.7rem; font-weight: 600; color: var(--color-text-muted, #64748b); }
.legend-items { display: flex; gap: 1rem; }
.legend-item { display: flex; align-items: center; gap: 0.375rem; }
.legend-color { width: 16px; height: 16px; border-radius: 0.25rem; border: 2px solid; }
.legend-color.full { background: rgba(34,211,238,0.2); border-color: #22d3ee; }
.legend-color.interrupted { background: rgba(239,68,68,0.2); border-color: #ef4444; }
.legend-color.instant { background: rgba(59,130,246,0.2); border-color: #3b82f6; }
.legend-color.swap { background: rgba(168,85,247,0.2); border-color: #a855f7; }
.legend-color.trait { background: rgba(245,158,11,0.2); border-color: #f59e0b; }
.legend-text { font-size: 0.65rem; color: var(--color-text-secondary, #94a3b8); }
.tooltip-enter-active, .tooltip-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.tooltip-enter-from, .tooltip-leave-to { opacity: 0; transform: translate(-50%, -100%) translateY(4px); }
@media (max-width: 768px) {
  .sr-header { flex-direction: column; align-items: stretch; }
  .sr-view-toggle { justify-content: center; }
  .track-header { width: 120px; }
  .timeline-ruler { padding-left: 120px; }
  .heatmap-label { width: 80px; }
  .filter-group { gap: 0.5rem; }
}
</style>
