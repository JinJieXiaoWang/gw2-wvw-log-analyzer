<template>
  <div class="detail-section">
    <h4 class="section-title">
      <i class="pi pi-percentage" /> 评分详情
    </h4>
    <div class="score-details">
      <div class="score-row">
        <span class="label">有效伤害</span><span class="value">{{ player.score_details.effectiveDamage }}</span>
      </div>
      <div class="score-row">
        <span class="label">CC伤害</span><span class="value">{{ player.score_details.breakbarDamage }}</span>
      </div>
      <div class="score-row">
        <span class="label">生存评分</span><span class="value">{{ player.score_details.survival }}</span>
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

.score-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.score-row {
  display: flex;
  justify-content: space-between;
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
}

.score-row .label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.score-row .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
