<template>
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
    <div
      v-for="(k, idx) in kpiList"
      :key="k.label"
      class="card p-4 rounded-xl border border-neutral-border/50 hover:border-primary/30 transition-all hover:shadow-lg group"
      :class="k.bg"
      :style="{ animationDelay: `${idx * ANIMATION_CONFIG.DELAY_STEP_MS}ms` }"
    >
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-medium text-neutral-text-secondary/80 uppercase">{{ k.label }}</span>
        <div class="p-2 rounded-lg bg-white/5 group-hover:bg-white/10 transition-colors">
          <i :class="k.icon + ' ' + k.color + ' text-lg'" />
        </div>
      </div>
      <div class="flex items-end">
        <p class="text-2xl font-bold text-neutral-text">
          {{ k.value }}
        </p>
        <span class="ml-2 text-xs text-neutral-text-secondary mb-1">{{ k.unit }}</span>
      </div>
      <div class="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-700"
          :class="k.barColor"
          :style="{ width: k.percent + '%' }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KpiItem } from '@/composables/combat/useCombatLogDetail'

const ANIMATION_CONFIG = {
  DELAY_STEP_MS: 100,
} as const

defineProps<{
  kpiList: KpiItem[]
}>()
</script>
