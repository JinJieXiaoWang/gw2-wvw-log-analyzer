<template>
  <div class="detail-section">
    <h4 class="section-title">
      <i class="pi pi-heart" /> 辅助统计
    </h4>
    <div class="support-stats">
      <div class="support-item">
        <i class="pi pi-star" /><span class="label">症状清除</span><span class="value">{{ player.cleanses }}</span>
      </div>
      <div class="support-item">
        <i class="pi pi-eye-slash" /><span class="label">增益剥离</span><span class="value">{{ player.strips }}</span>
      </div>
      <div class="support-item">
        <i class="pi pi-sync" /><span class="label">CC</span><span class="value">{{ player.cc }}</span>
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

.support-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.support-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.support-item i {
  font-size: 1.125rem;
  color: var(--color-primary);
}

.support-item .label {
  flex: 1;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.support-item .value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
}
</style>
