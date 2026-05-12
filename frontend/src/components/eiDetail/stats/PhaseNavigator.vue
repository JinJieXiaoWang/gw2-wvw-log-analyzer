<template>
  <div class="phase-navigator">
    <div class="phase-label">
      <i class="pi pi-sitemap" />
      <span>战斗阶段</span>
    </div>
    <div class="phase-list">
      <button
        v-for="(phase, index) in phases"
        :key="index"
        class="phase-btn"
        :class="{ active: activePhase === index, sub: phase.isSubPhase }"
        :title="phase.name"
        @click="$emit('select-phase', index)"
      >
        <span class="phase-name">{{ phase.name }}</span>
        <span class="phase-time">{{ formatPhaseTime(phase) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Phase } from '@/types/eliteInsights'

interface Props {
  phases: Phase[]
  activePhase: number
}

defineProps<Props>()

defineEmits<{
  (e: 'select-phase', index: number): void
}>()

function formatPhaseTime(phase: Phase): string {
  const startSec = Math.floor(phase.start)
  const endSec = Math.floor(phase.end)
  return `${startSec}s - ${endSec}s`
}
</script>

<style scoped lang="css">
.phase-navigator {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  margin-bottom: 1rem;
}

.phase-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
}

.phase-label i {
  color: var(--color-primary);
}

.phase-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.phase-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.125rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-bg);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
}

.phase-btn:hover {
  border-color: var(--color-primary-alpha-30);
  background-color: var(--color-card-hover);
}

.phase-btn.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 0 12px var(--color-primary-alpha-30);
}

.phase-btn.sub {
  font-size: 0.8125rem;
  padding: 0.375rem 0.625rem;
}

.phase-name {
  font-size: 0.8125rem;
  font-weight: 500;
}

.phase-time {
  font-size: 0.7rem;
  opacity: 0.8;
}
</style>
