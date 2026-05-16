<template>
  <div class="timeline-legend">
    <div class="legend-title">
      状态图例:
    </div>
    <div
      v-for="state in states"
      :key="state"
      class="legend-item"
    >
      <span
        class="legend-box"
        :class="`state-${state}`"
      /><span>{{ STATE_LABELS[state] }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { STATE_LABELS } from '@/utils/combat/rotation'

const states = ['full', 'interrupted', 'instant', 'swap', 'trait'] as const
</script>
