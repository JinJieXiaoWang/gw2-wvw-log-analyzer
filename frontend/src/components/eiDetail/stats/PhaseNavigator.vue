<template>
  <div class="phase-navigator flex items-center gap-4 p-[0.75rem 1.25rem] bg-neutral-card rounded-xl mb-4">
    <div class="phase-label flex items-center gap-2 text-sm font-semibold text-neutral-text whitespace-nowrap">
      <i class="pi pi-sitemap" />
      <span>战斗阶段</span>
    </div>
    <div class="phase-list flex gap-2 flex-wrap flex-1">
      <button
        v-for="(phase, index) in phases"
        :key="index"
        class="phase-btn flex flex-col items-center gap-0.5 rounded-lg bg-neutral-bg text-neutral-text-secondary cursor-pointer min-w-20"
        :class="[
          { active: activePhase === index },
          phase.isSubPhase ? 'text-[0.8125rem] py-1.5 px-2.5' : 'p-[0.5rem 0.875rem]'
        ]"
        :title="phase.name"
        @click="$emit('select-phase', index)"
      >
        <span class="phase-name text-[0.8125rem] font-medium">{{ phase.name }}</span>
        <span class="phase-time text-[0.7rem] opacity-80">{{ formatPhaseTime(phase) }}</span>
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
.phase-label i {
  color: var(--color-primary);
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
</style>
