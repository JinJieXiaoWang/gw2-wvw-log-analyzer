<script setup lang="ts">
/**
 * 伤害分布环形图组件
 * 功能：展示直伤/症状/破甲伤害占比
 * 更新：2026-05-11
 */

import { computed } from 'vue'
import type { EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'

const props = defineProps<{
  agg: EiAnalysisAggregate
}>()

const donut = computed(() => {
  const total = Math.max(props.agg.total_damage, 1)
  const p = Math.round((props.agg.total_power_damage / total) * 100)
  const c = Math.round((props.agg.total_condi_damage / total) * 100)
  const b = Math.round((props.agg.total_breakbar_damage / total) * 100)
  const circ = 2 * Math.PI * 40
  return {
    total: props.agg.total_damage,
    p, c, b,
    pd: `${(p / 100) * circ} ${circ}`,
    cd: `${(c / 100) * circ} ${circ}`,
    bd: `${(b / 100) * circ} ${circ}`,
    co: -((p / 100) * circ),
    bo: -(((p + c) / 100) * circ),
  }
})

const damageItems = computed(() => [
  { label: '直伤', value: props.agg.total_power_damage, percent: donut.value.p, color: '#FF4D6A' },
  { label: '症状', value: props.agg.total_condi_damage, percent: donut.value.c, color: '#FFAA00' },
  { label: '破甲', value: props.agg.total_breakbar_damage, percent: donut.value.b, color: '#165DFF' },
])
</script>

<template>
  <div class="card p-6 rounded-xl">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-neutral-text">
        伤害分布
      </h3>
      <span class="text-sm text-neutral-text-secondary">总计: {{ fmtCompact(donut.total) }}</span>
    </div>

    <div class="flex items-center gap-8">
      <div class="relative w-24 h-24">
        <svg
          viewBox="0 0 100 100"
          class="transform -rotate-90 w-full h-full"
        >
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#FF4D6A"
            stroke-width="12"
            :stroke-dasharray="donut.pd"
            class="transition-all duration-500"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#FFAA00"
            stroke-width="12"
            :stroke-dasharray="donut.cd"
            :stroke-dashoffset="donut.co"
            class="transition-all duration-500"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="#165DFF"
            stroke-width="12"
            :stroke-dasharray="donut.bd"
            :stroke-dashoffset="donut.bo"
            class="transition-all duration-500"
          />
          <circle
            cx="50"
            cy="50"
            r="32"
            fill="#2A2A2A"
          />
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-xs text-neutral-text-secondary">伤害类型</span>
        </div>
      </div>

      <div class="flex-1 space-y-3">
        <div
          v-for="item in damageItems"
          :key="item.label"
          class="flex items-center gap-3"
        >
          <div
            class="w-3 h-3 rounded-full"
            :style="{ backgroundColor: item.color }"
          />
          <span class="text-sm text-neutral-text-secondary w-8">{{ item.label }}</span>
          <span class="text-sm font-medium text-neutral-text">{{ item.percent }}%</span>
          <span class="text-xs text-neutral-text-secondary">{{ fmtCompact(item.value) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
