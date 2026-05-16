<template>
  <div class="detail-section">
    <h4 class="section-title">
      <i class="pi pi-shield" /> 生存统计
    </h4>
    <div class="survival-stats">
      <div class="survival-item">
        <i class="pi pi-exclamation-triangle" /><span class="label">倒地</span><span class="value">
          {{ player.downs }}</span>
      </div>
      <div class="survival-item">
        <i class="pi pi-times" /><span class="label">死亡</span><span class="value">{{ player.deaths }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights';

interface Props {
  player: Player
}

defineProps<Props>()
</script>

<style scoped lang="css">
.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.section-title i {
  color: var(--color-primary);
  font-size: 0.875rem;
}

.survival-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.survival-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.survival-item i {
  font-size: 1.125rem;
  color: var(--color-primary);
}

.survival-item .label {
  flex: 1;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.survival-item .value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
}
</style>
