<template>
  <div class="stat-group">
    <h4 class="group-title">
      <i class="pi pi-sparkles" />
      表现数据
    </h4>
    <div class="stat-items">
      <div class="stat-item">
        <span class="stat-label">暴击率</span>
        <span class="stat-value">{{ formatPercent(stats.criticalRate) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">侧身率</span>
        <span class="stat-value">{{ formatPercent(stats.flankingRate) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">技能浪费</span>
        <span class="stat-value">{{ stats.wasted }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">技能节约</span>
        <span class="stat-value">{{ stats.saved }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">武器切换</span>
        <span class="stat-value">{{ stats.swapCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PlayerStats } from '@/types/eliteInsights'
import { formatPercent } from '@/types/eliteInsights'

interface Props {
  stats: PlayerStats
}

defineProps<Props>()
</script>

<style scoped lang="css">
.stat-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
}

.group-title i {
  color: var(--color-accent);
}

.stat-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
