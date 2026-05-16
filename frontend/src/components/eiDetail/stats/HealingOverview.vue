<template>
  <div class="stats-overview">
    <div class="stat-card healing">
      <div class="stat-icon">
        <i class="pi pi-heart" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_TOTAL_HEALING }}</span>
        <span class="stat-value">{{ formatLargeNumber(totalHealing) }}</span>
      </div>
    </div>
    <div class="stat-card barrier">
      <div class="stat-icon">
        <i class="pi pi-shield" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_TOTAL_BARRIER }}</span>
        <span class="stat-value">{{ formatLargeNumber(totalBarrier) }}</span>
      </div>
    </div>
    <div class="stat-card hps">
      <div class="stat-icon">
        <i class="pi pi-gauge" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_AVG_HPS }}</span>
        <span class="stat-value">{{ formatLargeNumber(avgHps) }}</span>
      </div>
    </div>
    <div class="stat-card overheal">
      <div class="stat-icon">
        <i class="pi pi-chart-pie" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_OVERHEAL }}</span>
        <span class="stat-value">{{ overhealPercent }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  LABEL_TOTAL_HEALING,
  LABEL_TOTAL_BARRIER,
  LABEL_AVG_HPS,
  LABEL_OVERHEAL,
} from '@/constants/eiLabels'
import {
  COLOR_HEALING_START,
  COLOR_HEALING_END,
  COLOR_BARRIER_START,
  COLOR_BARRIER_END,
  COLOR_HPS_START,
  COLOR_HPS_END,
  COLOR_OVERHEAL_START,
  COLOR_OVERHEAL_END,
} from '@/constants/colors'
import { STAT_ICON_SIZE } from '@/constants/dimensions'

defineProps<{
  totalHealing: number
  totalBarrier: number
  avgHps: number
  overhealPercent: number
}>()

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
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.stat-icon {
  width: v-bind(STAT_ICON_SIZE);
  height: v-bind(STAT_ICON_SIZE);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
}

.stat-card.healing .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_HEALING_START), v-bind(COLOR_HEALING_END));
}

.stat-card.barrier .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_BARRIER_START), v-bind(COLOR_BARRIER_END));
}

.stat-card.hps .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_HPS_START), v-bind(COLOR_HPS_END));
}

.stat-card.overheal .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_OVERHEAL_START), v-bind(COLOR_OVERHEAL_END));
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}
</style>
