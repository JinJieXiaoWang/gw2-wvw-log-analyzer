<template>
  <div class="stat-group">
    <h4 class="group-title">
      <i class="pi pi-bolt" />
      伤害数据
    </h4>
    <div class="stat-items">
      <div class="stat-item">
        <span class="stat-label">总伤害</span>
        <span class="stat-value">{{ formatDamage(dps.damage) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">DPS</span>
        <span class="stat-value">{{ formatDamage(dps.dps) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">直伤</span>
        <span class="stat-value">{{ formatDamage(dps.powerDamage) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">症状</span>
        <span class="stat-value">{{ formatDamage(dps.condiDamage) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">破控伤害</span>
        <span class="stat-value">{{ formatDamage(dps.breakbarDamage) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PlayerDps } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'

interface Props {
  dps: PlayerDps
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
