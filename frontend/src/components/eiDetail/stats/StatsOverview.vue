<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
    <div class="stat-card damage">
      <div class="stat-icon">
        <i class="pi pi-bolt" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_TOTAL_DAMAGE }}</span>
        <span class="stat-value">{{ formatLargeNumber(totalDamage) }}</span>
      </div>
    </div>
    <div class="stat-card dps">
      <div class="stat-icon">
        <i class="pi pi-gauge" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_AVG_DPS }}</span>
        <span class="stat-value">{{ formatLargeNumber(avgDps) }}</span>
      </div>
    </div>
    <div class="stat-card survival">
      <div class="stat-icon">
        <i class="pi pi-heart" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_ALIVE_PLAYERS }}</span>
        <span class="stat-value">{{ alivePlayers }}/{{ totalPlayers }}</span>
      </div>
    </div>
    <div class="stat-card score">
      <div class="stat-icon">
        <i class="pi pi-trophy" />
      </div>
      <div class="stat-info">
        <span class="stat-label">{{ LABEL_TEAM_SCORE }}</span>
        <span class="stat-value">{{ teamScore }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  LABEL_TOTAL_DAMAGE,
  LABEL_AVG_DPS,
  LABEL_ALIVE_PLAYERS,
  LABEL_TEAM_SCORE,
} from '@/constants/eiLabels'
import {
  COLOR_DAMAGE_START,
  COLOR_DAMAGE_END,
  COLOR_DPS_START,
  COLOR_DPS_END,
  COLOR_SCORE_START,
  COLOR_SCORE_END,
  COLOR_CLEANSE_START,
  COLOR_CLEANSE_END,
} from '@/constants/colors'
import { STAT_ICON_SIZE } from '@/constants/dimensions'

defineProps<{
  totalDamage: number
  avgDps: number
  alivePlayers: number
  totalPlayers: number
  teamScore: number
}>()

function formatLargeNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped lang="css">
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

.stat-card.damage .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_DAMAGE_START), v-bind(COLOR_DAMAGE_END));
}

.stat-card.dps .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_DPS_START), v-bind(COLOR_DPS_END));
}

.stat-card.survival .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_CLEANSE_START), v-bind(COLOR_CLEANSE_END));
}

.stat-card.score .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_SCORE_START), v-bind(COLOR_SCORE_END));
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
