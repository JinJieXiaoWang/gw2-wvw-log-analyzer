<template>
  <div class="graph-summary card">
    <div class="summary-grid">
      <div class="summary-item">
        <span class="summary-label">峰值DPS</span>
        <span class="summary-value">{{ formatDamage(peakDps) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">平均DPS</span>
        <span class="summary-value">{{ formatDamage(avgDps) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">最低DPS</span>
        <span class="summary-value">{{ formatDamage(minDps) }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">波动幅度</span>
        <span class="summary-value">{{ formatDamage(peakDps - minDps) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDamage } from '@/types/eliteInsights'

defineProps<{
  peakDps: number
  avgDps: number
  minDps: number
}>()
</script>

<style scoped lang="css">
.graph-summary {
  padding: 1rem 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}
</style>
