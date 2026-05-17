<template>
  <div class="detail-section">
    <h4 class="section-title">
      {{ SECTION_BATTLE_DETAILS }}
    </h4>
    <div class="detail-grid">
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_DIRECT_DAMAGE }}</span>
        <span class="detail-value">{{ formatLargeNumber(player.dpsAll?.[0]?.powerDamage || 0) }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_CONDITION_DAMAGE }}</span>
        <span class="detail-value">{{ formatLargeNumber(player.dpsAll?.[0]?.condiDamage || 0) }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_CRIT_RATE }}</span>
        <span class="detail-value">{{ player.critRate || 0 }}%</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_CRIT_DAMAGE }}</span>
        <span class="detail-value">{{ player.critDamage || 0 }}%</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_PRECISION }}</span>
        <span class="detail-value">{{ player.precision || 0 }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_POWER }}</span>
        <span class="detail-value">{{ player.power || 0 }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_TOUGHNESS }}</span>
        <span class="detail-value">{{ player.toughness || 0 }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">{{ LABEL_VITALITY }}</span>
        <span class="detail-value">{{ player.vitality || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import {
  SECTION_BATTLE_DETAILS,
  LABEL_DIRECT_DAMAGE,
  LABEL_CONDITION_DAMAGE,
  LABEL_CRIT_RATE,
  LABEL_CRIT_DAMAGE,
  LABEL_PRECISION,
  LABEL_POWER,
  LABEL_TOUGHNESS,
  LABEL_VITALITY,
} from '@/constants/eiLabels'

defineProps<{
  player: Player
}>()

function formatLargeNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped lang="css">
.detail-section { margin-bottom: 1.5rem; }

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.25rem;
}

.detail-label { font-size: 0.8125rem; color: var(--color-text-secondary); }
.detail-value { font-size: 0.8125rem; font-weight: 600; color: var(--color-text); }
</style>
