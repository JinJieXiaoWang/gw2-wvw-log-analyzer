<template>
  <div class="stats-grid">
    <div class="stat-box damage">
      <div class="stat-icon"><i class="pi pi-bolt" /></div>
      <div class="stat-data">
        <span class="stat-value">{{ formatLargeNumber(player.dpsAll?.[0]?.damage || 0) }}</span>
        <span class="stat-label">{{ LABEL_TOTAL_DAMAGE }}</span>
      </div>
    </div>
    <div class="stat-box dps">
      <div class="stat-icon"><i class="pi pi-gauge" /></div>
      <div class="stat-data">
        <span class="stat-value">{{ player.dps }}</span>
        <span class="stat-label">{{ LABEL_DPS }}</span>
      </div>
    </div>
    <div class="stat-box score">
      <div class="stat-icon"><i class="pi pi-trophy" /></div>
      <div class="stat-data">
        <span class="stat-value">{{ player.total_score }}</span>
        <span class="stat-label">{{ LABEL_SCORE }}</span>
      </div>
    </div>
    <div class="stat-box cleanse">
      <div class="stat-icon"><i class="pi pi-minus-circle" /></div>
      <div class="stat-data">
        <span class="stat-value">{{ player.support?.[0]?.condiCleanse || 0 }}</span>
        <span class="stat-label">{{ LABEL_CLEANSE }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import {
  LABEL_TOTAL_DAMAGE,
  LABEL_DPS,
  LABEL_SCORE,
  LABEL_CLEANSE,
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
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
}

.stat-box.damage .stat-icon { background: linear-gradient(135deg, v-bind(COLOR_DAMAGE_START), v-bind(COLOR_DAMAGE_END)); }
.stat-box.dps .stat-icon { background: linear-gradient(135deg, v-bind(COLOR_DPS_START), v-bind(COLOR_DPS_END)); }
.stat-box.score .stat-icon { background: linear-gradient(135deg, v-bind(COLOR_SCORE_START), v-bind(COLOR_SCORE_END)); }
.stat-box.cleanse .stat-icon { background: linear-gradient(135deg, v-bind(COLOR_CLEANSE_START), v-bind(COLOR_CLEANSE_END)); }

.stat-icon i { font-size: 1.25rem; color: white; }

.stat-data { display: flex; flex-direction: column; }

.stat-value { font-size: 1.25rem; font-weight: 700; color: var(--color-text); }
.stat-label { font-size: 0.7rem; color: var(--color-text-secondary); }
</style>
