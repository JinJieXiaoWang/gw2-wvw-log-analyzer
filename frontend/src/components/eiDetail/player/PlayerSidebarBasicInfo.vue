<template>
  <div class="detail-section">
    <h4 class="section-title">
      <i class="pi pi-info-circle" /> 基本信息
    </h4>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">职业</span><span class="value">{{ getProfName(player.profession) }}</span>
      </div>
      <div class="info-item">
        <span class="label">分组</span><span class="value">{{ player.group }}</span>
      </div>
      <div class="info-item">
        <span class="label">评分</span><span class="value score">{{ player.total_score }}</span>
      </div>
      <div class="info-item">
        <span class="label">角色</span><span class="value">{{ player.role }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights';
import { getProfessionName } from '@/utils/profession/professionUtils';

interface Props {
  player: Player
}

defineProps<Props>()

function getProfName(prof: string) {
  return getProfessionName(prof)
}
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.info-item .label {
  font-size: 0.7rem;
  color: var(--color-text-disabled);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.info-item .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.info-item .value.score {
  color: var(--color-primary);
  font-size: 1.125rem;
}
</style>
