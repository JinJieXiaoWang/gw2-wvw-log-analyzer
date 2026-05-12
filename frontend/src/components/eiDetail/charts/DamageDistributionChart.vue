<template>
  <div class="damage-distribution-card bg-neutral-card rounded-xl p-5">
    <div class="card-header mb-4">
      <h3 class="card-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
        <i class="pi pi-pie-chart text-[var(--color-accent)]" />
        伤害分布
      </h3>
    </div>
    <div class="card-content flex items-center gap-8">
      <div class="donut-chart flex items-center gap-8">
        <div class="chart-circle relative w-[140px] h-[140px]">
          <svg
            viewBox="0 0 100 100"
            class="donut-svg w-full h-full"
          >
            <!-- 直伤部分 -->
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              :stroke="powerColor"
              stroke-width="12"
              :stroke-dasharray="powerDashArray"
              stroke-dashoffset="0"
              transform="rotate(-90 50 50)"
              class="donut-segment transition-[stroke-dasharray] duration-500 ease-[ease]"
            />
            <!-- 症状部分 -->
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              :stroke="condiColor"
              stroke-width="12"
              :stroke-dasharray="condiDashArray"
              :stroke-dashoffset="condiOffset"
              transform="rotate(-90 50 50)"
              class="donut-segment transition-[stroke-dasharray] duration-500 ease-[ease]"
            />
            <!-- 破甲部分 -->
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              :stroke="breakbarColor"
              stroke-width="12"
              :stroke-dasharray="breakbarDashArray"
              :stroke-dashoffset="breakbarOffset"
              transform="rotate(-90 50 50)"
              class="donut-segment transition-[stroke-dasharray] duration-500 ease-[ease]"
            />
          </svg>
          <div class="chart-center absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2 text-center">
            <span class="center-value block text-xl font-bold text-neutral-text">{{ formatLargeNumber(total) }}</span>
            <span class="center-label block text-xs text-neutral-text-secondary">总伤害</span>
          </div>
        </div>
        <div class="chart-legend flex flex-col gap-3">
          <div class="legend-item flex items-center gap-2">
            <span
              class="legend-color w-4 h-4 rounded-[4px]"
              :style="{ backgroundColor: powerColor }"
            />
            <span class="legend-label text-sm text-neutral-text-secondary">直伤</span>
            <span class="legend-value ml-[auto] text-sm font-semibold text-neutral-text">{{ powerPercent }}%</span>
          </div>
          <div class="legend-item flex items-center gap-2">
            <span
              class="legend-color w-4 h-4 rounded-[4px]"
              :style="{ backgroundColor: condiColor }"
            />
            <span class="legend-label text-sm text-neutral-text-secondary">症状</span>
            <span class="legend-value ml-[auto] text-sm font-semibold text-neutral-text">{{ condiPercent }}%</span>
          </div>
          <div class="legend-item flex items-center gap-2">
            <span
              class="legend-color w-4 h-4 rounded-[4px]"
              :style="{ backgroundColor: breakbarColor }"
            />
            <span class="legend-label text-sm text-neutral-text-secondary">破甲</span>
            <span class="legend-value ml-[auto] text-sm font-semibold text-neutral-text">{{ breakbarPercent }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Colors } from '@/config/designTokens'

const props = defineProps<{
  powerDamage: number
  condiDamage: number
  breakbarDamage: number
}>()

const powerColor = Colors.palette.blue
const condiColor = Colors.palette.green
const breakbarColor = Colors.palette.amber

const total = computed(() => {
  return props.powerDamage + props.condiDamage + props.breakbarDamage
})

const powerPercent = computed(() => {
  if (total.value === 0) return 0
  return Math.round((props.powerDamage / total.value) * 100)
})

const condiPercent = computed(() => {
  if (total.value === 0) return 0
  return Math.round((props.condiDamage / total.value) * 100)
})

const breakbarPercent = computed(() => {
  if (total.value === 0) return 0
  return Math.round((props.breakbarDamage / total.value) * 100)
})

const circumference = 2 * Math.PI * 40

const powerDashArray = computed(() => {
  const length = (powerPercent.value / 100) * circumference
  return `${length} ${circumference}`
})

const condiDashArray = computed(() => {
  const length = (condiPercent.value / 100) * circumference
  return `${length} ${circumference}`
})

const condiOffset = computed(() => {
  return -(powerPercent.value / 100) * circumference
})

const breakbarDashArray = computed(() => {
  const length = (breakbarPercent.value / 100) * circumference
  return `${length} ${circumference}`
})

const breakbarOffset = computed(() => {
  return -((powerPercent.value + condiPercent.value) / 100) * circumference
})

function formatLargeNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

