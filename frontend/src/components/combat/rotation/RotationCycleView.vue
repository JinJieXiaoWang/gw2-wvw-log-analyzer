<template>
  <div class="sr-cycle-view">
    <div class="cycle-container">
      <div v-for="(cycle, cycleIdx) in cycles" :key="cycleIdx" class="cycle-card">
        <div class="cycle-header">
          <div class="cycle-badge">
            <span class="cycle-number">{{ cycleIdx + 1 }}</span>
            <span class="cycle-duration">{{ formatCycleTime(cycle.duration) }}</span>
          </div>
          <div class="cycle-stats">
            <span class="stat-item"><span class="stat-label">技能</span><span class="stat-value">{{ cycle.events.length }}</span></span>
            <span class="stat-item"><span class="stat-label">打断</span><span class="stat-value interrupted">{{ cycle.interruptedCount }}</span></span>
          </div>
        </div>
        <div class="cycle-skills-flow">
          <div class="flow-line" />
          <div
            v-for="(evt, idx) in cycle.events"
            :key="idx"
            class="skill-node"
            :class="[`state-${evt.state}`, { 'is-auto': evt.autoAttack, 'is-swap': evt.isSwap, 'is-instant': evt.isInstant, 'is-trait': evt.isTraitProc }]"
            @mouseenter="$emit('hover-skill', evt)"
            @mousemove="$emit('mousemove', $event)"
            @mouseleave="$emit('leave-skill')"
          >
            <div class="skill-icon-wrapper">
              <img v-if="evt.icon" :src="evt.icon" :alt="evt.name" class="skill-icon" loading="lazy">
              <div v-else class="skill-placeholder">{{ evt.name?.charAt(0) || '?' }}</div>
              <div v-if="evt.state === 'interrupted'" class="state-badge interrupted"><i class="pi pi-times" /></div>
              <div v-else-if="evt.isInstant" class="state-badge instant">!</div>
            </div>
            <div class="skill-label">{{ evt.name }}</div>
            <div class="skill-time">{{ formatTime(evt.castTime) }}</div>
          </div>
        </div>
      </div>
    </div>
    <EmptyState v-if="cycles.length === 0" icon="pi pi-inbox" title="暂无技能循环数据" />
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
.sr-cycle-view { display: flex; flex-direction: column; gap: 0.75rem; }
.cycle-container { display: flex; flex-direction: column; gap: 0.75rem; }
.cycle-card { background: rgba(255,255,255,0.03); border-radius: 0.5rem; padding: 0.75rem; border: 1px solid rgba(255,255,255,0.05); }
.cycle-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.cycle-badge { display: flex; align-items: center; gap: 0.5rem; }
.cycle-number { width: 28px; height: 28px; border-radius: 0.375rem; background: linear-gradient(135deg, #3b82f6, #8b5cf6); display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75rem; font-weight: 700; }
.cycle-duration { font-size: 0.7rem; color: var(--color-text-muted, #64748b); font-family: monospace; }
.cycle-stats { display: flex; gap: 1rem; }
.stat-item { display: flex; flex-direction: column; align-items: flex-end; }
.stat-label { font-size: 0.6rem; color: var(--color-text-muted, #64748b); }
.stat-value { font-size: 0.75rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); }
.stat-value.interrupted { color: #ef4444; }
.cycle-skills-flow { position: relative; display: flex; align-items: center; gap: 0.375rem; padding-left: 0.25rem; flex-wrap: wrap; }
.flow-line { position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, rgba(59,130,246,0.3), rgba(139,92,246,0.3)); transform: translateY(-50%); z-index: 0; }
.skill-node { position: relative; display: flex; flex-direction: column; align-items: center; gap: 0.25rem; z-index: 1; transition: transform 0.2s ease; }
.skill-node:hover { transform: translateY(-4px); }
.skill-icon-wrapper { position: relative; width: 36px; height: 36px; border-radius: 0.375rem; overflow: hidden; border: 2px solid rgba(255,255,255,0.1); transition: border-color 0.2s; }
.skill-node.state-full .skill-icon-wrapper { border-color: #22d3ee; box-shadow: 0 0 8px rgba(34,211,238,0.3); }
.skill-node.state-interrupted .skill-icon-wrapper { border-color: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.3); }
.skill-node.state-instant .skill-icon-wrapper { border-color: #3b82f6; box-shadow: 0 0 8px rgba(59,130,246,0.3); }
.skill-node.state-swap .skill-icon-wrapper { border-color: #a855f7; background: rgba(168,85,247,0.15); }
.skill-node.state-trait .skill-icon-wrapper { border-color: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.3); }
.skill-node.is-auto .skill-icon-wrapper { opacity: 0.7; transform: scale(0.85); }
.skill-icon { width: 100%; height: 100%; object-fit: cover; }
.skill-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.05); font-size: 0.875rem; font-weight: 700; color: var(--color-text-secondary, #94a3b8); }
.state-badge { position: absolute; top: -4px; right: -4px; width: 16px; height: 16px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.55rem; font-weight: 800; color: white; }
.state-badge.interrupted { background: #ef4444; }
.state-badge.instant { background: #3b82f6; }
.skill-label { font-size: 0.65rem; color: var(--color-text-secondary, #94a3b8); text-align: center; max-width: 48px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.skill-time { font-size: 0.6rem; color: var(--color-text-muted, #64748b); font-family: monospace; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem; color: var(--color-text-muted, #64748b); }
.empty-icon { font-size: 3rem; margin-bottom: 0.5rem; opacity: 0.5; }
.empty-state p { font-size: 0.875rem; }
</style>
