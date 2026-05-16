<template>
  <div
    v-if="hoveredSkill && tooltipPosition"
    class="fixed z-50 p-3 rounded-lg bg-neutral-card border border-neutral-border shadow-xl pointer-events-none"
    :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
  >
    <div class="flex items-center gap-2 mb-2">
      <img
        v-if="hoveredSkill.icon"
        :src="hoveredSkill.icon"
        class="w-6 h-6 rounded"
      >
      <span class="font-semibold text-neutral-text">{{ hoveredSkill.name }}</span>
    </div>
    <div class="text-xs text-neutral-text-secondary space-y-1">
      <p v-if="hoveredSkill.count">
        {{ LABELS.CAST_COUNT }} {{ hoveredSkill.count }}
      </p>
      <p v-if="hoveredSkill.time !== undefined">
        {{ LABELS.TIME }} {{ hoveredSkill.time.toFixed(1) }}s
      </p>
      <p v-if="hoveredSkill.duration">
        {{ LABELS.DURATION }} {{ hoveredSkill.duration }}ms
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const LABELS = {
  CAST_COUNT: '释放次数:',
  TIME: '时间:',
  DURATION: '持续时间:',
} as const

defineProps<{
  hoveredSkill: any
  tooltipPosition: { x: number; y: number } | null
}>()
</script>
