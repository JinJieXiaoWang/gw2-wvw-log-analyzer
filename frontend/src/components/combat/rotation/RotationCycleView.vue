<template>
  <div class="sr-cycle-view flex flex-col gap-3">
    <div class="cycle-container flex flex-col gap-3">
      <div
        v-for="(cycle, cycleIdx) in cycles"
        :key="cycleIdx"
        class="cycle-card bg-white/[0.03] rounded-lg p-3 border border-white/[0.05]"
      >
        <div class="cycle-header flex justify-between items-center mb-3">
          <div class="cycle-badge flex items-center gap-2">
            <span class="cycle-number w-7 h-7 rounded-md flex items-center justify-center text-white text-xs font-bold">{{ cycleIdx + 1 }}</span>
            <span class="cycle-duration text-[0.7rem] text-[var(--color-text-muted,#64748b)] font-mono">{{ formatCycleTime(cycle.duration) }}</span>
          </div>
          <div class="cycle-stats flex gap-4">
            <span class="stat-item flex flex-col items-end"><span class="stat-label text-[0.6rem] text-[var(--color-text-muted,#64748b)]">技能</span><span class="stat-value text-xs font-semibold text-[var(--color-text-primary,#f1f5f9)]">{{ cycle.events.length }}</span></span>
            <span class="stat-item flex flex-col items-end"><span class="stat-label text-[0.6rem] text-[var(--color-text-muted,#64748b)]">打断</span><span class="stat-value interrupted text-xs font-semibold text-[var(--color-text-primary,#f1f5f9)]">{{ cycle.interruptedCount }}</span></span>
          </div>
        </div>
        <div class="cycle-skills-flow relative flex items-center gap-1.5 pl-1 flex-wrap">
          <div class="flow-line absolute top-1/2 left-0 right-0 h-0.5 -translate-y-1/2 z-0" />
          <div
            v-for="(evt, idx) in cycle.events"
            :key="idx"
            class="skill-node relative flex flex-col items-center gap-1 z-[1] transition-transform duration-200"
            :class="[`state-${evt.state}`, { 'is-auto': evt.autoAttack, 'is-swap': evt.isSwap, 'is-instant': evt.isInstant, 'is-trait': evt.isTraitProc }]"
            @mouseenter="$emit('hover-skill', evt)"
            @mousemove="$emit('mousemove', $event)"
            @mouseleave="$emit('leave-skill')"
          >
            <div class="skill-icon-wrapper relative w-9 h-9 rounded-md overflow-hidden border-2 border-white/10 transition-colors duration-200">
              <img
                v-if="evt.icon"
                :src="evt.icon"
                :alt="evt.name"
                class="skill-icon w-full h-full object-cover"
                loading="lazy"
              >
              <div
                v-else
                class="skill-placeholder w-full h-full flex items-center justify-center bg-white/5 text-sm font-bold text-[var(--color-text-secondary,#94a3b8)]"
              >
                {{ evt.name?.charAt(0) || '?' }}
              </div>
              <div
                v-if="evt.state === 'interrupted'"
                class="state-badge interrupted absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-[0.55rem] font-extrabold text-white"
              >
                <i class="pi pi-times" />
              </div>
              <div
                v-else-if="evt.isInstant"
                class="state-badge instant absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-[0.55rem] font-extrabold text-white"
              >
                !
              </div>
            </div>
            <div class="skill-label text-[0.65rem] text-[var(--color-text-secondary,#94a3b8)] text-center max-w-12 overflow-hidden text-ellipsis whitespace-nowrap">
              {{ evt.name }}
            </div>
            <div class="skill-time text-[0.6rem] text-[var(--color-text-muted,#64748b)] font-mono">
              {{ formatTime(evt.castTime) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <EmptyState
      v-if="cycles.length === 0"
      icon="pi pi-inbox"
      title="暂无技能循环数据"
    />
  </div>
</template>

<script setup lang="ts">
import type { SkillCycle } from '@/utils/combat/rotationTypes'
import { formatTime, formatCycleTime } from '@/utils/combat/rotation'

defineProps<{ cycles: SkillCycle[] }>()
defineEmits<{
  'hover-skill': [skill: any]
  'leave-skill': []
  'mousemove': [event: MouseEvent]
}>()
</script>

<style scoped>
.cycle-number { background: linear-gradient(135deg, #3b82f6, #8b5cf6); }
.flow-line { background: linear-gradient(90deg, rgba(59,130,246,0.3), rgba(139,92,246,0.3)); }
.skill-node:hover { transform: translateY(-4px); }
.skill-node.state-full .skill-icon-wrapper { border-color: #22d3ee; box-shadow: 0 0 8px rgba(34,211,238,0.3); }
.skill-node.state-interrupted .skill-icon-wrapper { border-color: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.3); }
.skill-node.state-instant .skill-icon-wrapper { border-color: #3b82f6; box-shadow: 0 0 8px rgba(59,130,246,0.3); }
.skill-node.state-swap .skill-icon-wrapper { border-color: #a855f7; background: rgba(168,85,247,0.15); }
.skill-node.state-trait .skill-icon-wrapper { border-color: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.3); }
.skill-node.is-auto .skill-icon-wrapper { opacity: 0.7; transform: scale(0.85); }
.stat-value.interrupted { color: #ef4444; }
.state-badge.interrupted { background: #ef4444; }
.state-badge.instant { background: #3b82f6; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem; color: var(--color-text-muted, #64748b); }
.empty-icon { font-size: 3rem; margin-bottom: 0.5rem; opacity: 0.5; }
.empty-state p { font-size: 0.875rem; }
</style>
