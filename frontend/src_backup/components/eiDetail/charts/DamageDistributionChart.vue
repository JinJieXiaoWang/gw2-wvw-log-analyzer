<template>
  <div class="damage-distribution-card">
    <div class="card-header">
      <h3 class="card-title">
        <i class="pi pi-pie-chart" />
        伤害分布
      </h3>
    </div>
    <div class="card-content">
      <div class="donut-chart">
        <div class="chart-circle">
          <svg
            viewBox="0 0 100 100"
            class="donut-svg"
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
              class="donut-segment"
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
              class="donut-segment"
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
              class="donut-segment"
            />
          </svg>
          <div class="chart-center">
            <span class="center-value">{{ formatLargeNumber(total) }}</span>
            <span class="center-label">总伤害</span>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item">
            <span
              class="legend-color"
              :style="{ backgroundColor: powerColor }"
            />
            <span class="legend-label">直伤</span>
            <span class="legend-value">{{ powerPercent }}%</span>
          </div>
          <div class="legend-item">
            <span
              class="legend-color"
              :style="{ backgroundColor: condiColor }"
            />
            <span class="legend-label">症状</span>
            <span class="legend-value">{{ condiPercent }}%</span>
          </div>
          <div class="legend-item">
            <span
              class="legend-color"
              :style="{ backgroundColor: breakbarColor }"
            />
            <span class="legend-label">破甲</span>
            <span class="legend-value">{{ breakbarPercent }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  powerDamage: number
  condiDamage: number
  breakbarDamage: number
}>()

const powerColor = '#3b82f6'
const condiColor = '#22c55e'
const breakbarColor = '#f59e0b'

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

<style scoped lang="css">
.damage-distribution-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.card-header {
  margin-bottom: 1rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.card-title i {
  color: var(--color-accent);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.donut-chart {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.chart-circle {
  position: relative;
  width: 140px;
  height: 140px;
}

.donut-svg {
  width: 100%;
  height: 100%;
}

.donut-segment {
  transition: stroke-dasharray 0.5s ease;
}

.chart-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.center-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}

.center-label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.legend-value {
  margin-left: auto;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>