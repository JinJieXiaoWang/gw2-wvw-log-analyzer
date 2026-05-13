<template>
  <div class="skill-rotation-timeline">
    <RotationViewModeBar
      v-model:view-mode="viewMode"
      v-model:show-auto-attacks="showAutoAttacks"
      v-model:show-instant-cast="showInstantCast"
    />
    <RotationCycleView
      v-if="viewMode === 'simple'"
      :cycles="mappedCycles"
      show-swap-icon
      @hover-skill="hoveredSkill = $event"
      @mousemove="handleMouseMove"
      @leave-skill="hoveredSkill = null"
    />
    <RotationTimelineView
      v-else
      :ticks="advancedTimeTicks"
      :tracks="mappedTracks"
      min-track-width="800px"
      show-bar-icons
      show-grid-lines
      @hover-skill="hoveredSkill = $event"
      @mousemove="handleMouseMove"
      @leave-skill="hoveredSkill = null"
    />
    <RotationTimelineLegend />

    <!-- Tooltip -->
    <Transition name="tooltip-fade">
      <div
        v-if="hoveredSkill"
        class="fixed z-[1000] pointer-events-none bg-[rgba(15,23,42,0.98)] border border-white/10 rounded-lg p-2.5 min-w-[200px] shadow-xl"
        :style="tooltipStyle"
      >
        <div class="flex items-center gap-2 mb-2 pb-2 border-b border-white/[0.08]">
          <img
            v-if="hoveredSkill.icon"
            :src="hoveredSkill.icon"
            class="w-8 h-8 rounded"
          >
          <div class="flex flex-col gap-0.5">
            <span class="text-sm font-bold text-[#f1f5f9]">{{ hoveredSkill.name }}</span>
            <span
              class="text-[0.65rem] px-1.5 py-0.5 rounded w-fit"
              :style="getStateStyle(hoveredSkill.state)"
            >{{ STATE_LABELS[hoveredSkill.state] || hoveredSkill.state }}</span>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <div class="flex justify-between text-[0.7rem]">
            <span class="text-[#94a3b8]">施放时间</span>
            <span class="text-[#f1f5f9] font-medium">{{ formatTime(hoveredSkill.castTime) }}</span>
          </div>
          <div class="flex justify-between text-[0.7rem]">
            <span class="text-[#94a3b8]">持续时间</span>
            <span class="text-[#f1f5f9] font-medium">{{ hoveredSkill.duration }}ms</span>
          </div>
          <div
            v-if="hoveredSkill.timeGained !== 0"
            class="flex justify-between text-[0.7rem]"
          >
            <span class="text-[#94a3b8]">动画差</span>
            <span
              class="font-medium"
              :class="hoveredSkill.timeGained < 0 ? 'text-[#ef4444]' : 'text-[#f1f5f9]'"
            >{{ hoveredSkill.timeGained > 0 ? '+' : '' }}{{ hoveredSkill.timeGained }}ms</span>
          </div>
          <div class="flex justify-between text-[0.7rem]">
            <span class="text-[#94a3b8]">急速</span>
            <span class="text-[#f1f5f9] font-medium">{{ Math.round((hoveredSkill.quickness || 0) * 100) }}%</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSkillRotationTimeline, type RotationEvent } from '@/composables/combat/useSkillRotationTimeline'
import { STATE_LABELS, formatTime } from '@/utils/combat/rotation'
import type { SkillCycle, SkillTrack, CycleEvent } from '@/utils/combat/rotationTypes'
import RotationViewModeBar from './rotation/RotationViewModeBar.vue'
import RotationCycleView from './rotation/RotationCycleView.vue'
import RotationTimelineView from './rotation/RotationTimelineView.vue'
import RotationTimelineLegend from './rotation/RotationTimelineLegend.vue'

const props = defineProps<{
  events: RotationEvent[]
  fightDuration?: number
}>()

const {
  viewMode, showAutoAttacks, showInstantCast,
  simpleCycles, advancedSkillRows, advancedTimeTicks, flatEvents,
} = useSkillRotationTimeline(props)

const hoveredSkill = ref<any>(null)
const tooltipX = ref(0)
const tooltipY = ref(0)

const tooltipStyle = computed(() => ({
  left: `${tooltipX.value}px`,
  top: `${tooltipY.value}px`,
  transform: 'translate(-50%, -100%) translateY(-8px)',
}))

const mappedCycles = computed<SkillCycle[]>(() =>
  simpleCycles.value.map(cycle => ({
    duration: cycle.duration,
    events: cycle.events.map(evt => ({
      ...evt,
      state: (evt.isSwap
        ? 'swap'
        : evt.isTraitProc
          ? 'trait'
          : evt.state === 'unknown'
            ? 'full'
            : evt.state) as CycleEvent['state'],
    })),
    interruptedCount: cycle.events.filter(e => e.state === 'interrupted').length,
  })),
)

const mappedTracks = computed<SkillTrack[]>(() =>
  advancedSkillRows.value.map(row => ({
    skillId: row.skillId,
    name: row.name,
    icon: row.icon,
    casts: row.casts.map(cast => {
      const evt = flatEvents.value.find(
        e => String(e.skillId) === String(row.skillId) && e.castTime === cast.castTime,
      )
      return {
        castTime: cast.castTime,
        duration: cast.duration,
        state: (cast.state === 'unknown' ? 'full' : cast.state) as CycleEvent['state'],
        position: cast.left,
        width: cast.width,
        skillId: row.skillId,
        timeGained: evt?.timeGained ?? 0,
        quickness: evt?.quickness ?? 0,
        name: row.name,
        icon: row.icon,
      }
    }),
  })),
)

function handleMouseMove(event: MouseEvent) {
  tooltipX.value = event.clientX + 16
  tooltipY.value = event.clientY + 16
}

function getStateStyle(state: string) {
  const map: Record<string, { background: string; color: string }> = {
    full: { background: 'rgba(34,211,238,0.15)', color: '#22d3ee' },
    interrupted: { background: 'rgba(239,68,68,0.15)', color: '#ef4444' },
    instant: { background: 'rgba(59,130,246,0.15)', color: '#3b82f6' },
    swap: { background: 'rgba(168,85,247,0.15)', color: '#a855f7' },
    trait: { background: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
  }
  return map[state] || { background: 'rgba(255,255,255,0.1)', color: '#e2e8f0' }
}
</script>

<style scoped src="@/styles/components/combat/SkillRotationTimeline.css"></style>
<style scoped>
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.15s ease;
}
.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}
</style>
