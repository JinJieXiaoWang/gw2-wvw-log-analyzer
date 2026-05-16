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
        <DonutChart
          :config="{ size: 140, strokeWidth: 12, radius: 40 }"
          :segments="[
            { color: powerColor, value: powerDamage },
            { color: condiColor, value: condiDamage },
            { color: breakbarColor, value: breakbarDamage },
          ]"
        >
          <span class="center-value">{{ formatLargeNumber(total) }}</span>
          <span class="center-label">总伤害</span>
        </DonutChart>
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
import DonutChart from '@/components/common/charts/DonutChart.vue'

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