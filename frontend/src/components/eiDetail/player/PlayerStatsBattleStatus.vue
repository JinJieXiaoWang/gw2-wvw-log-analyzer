<template>
  <div class="status-section">
    <h4 class="section-title">{{ SECTION_BATTLE_STATUS }}</h4>
    <div class="status-grid">
      <div class="status-item" :class="{ danger: player.downs > 0 }">
        <i class="pi pi-skull-crossbones" />
        <div class="status-data">
          <span class="status-value">{{ player.downs }}</span>
          <span class="status-label">{{ LABEL_DOWNS }}</span>
        </div>
      </div>
      <div class="status-item" :class="{ danger: player.deaths > 0 }">
        <i class="pi pi-heart-broken" />
        <div class="status-data">
          <span class="status-value">{{ player.deaths }}</span>
          <span class="status-label">{{ LABEL_DEATHS }}</span>
        </div>
      </div>
      <div class="status-item">
        <i class="pi pi-shield" />
        <div class="status-data">
          <span class="status-value">{{ player.cc }}</span>
          <span class="status-label">{{ LABEL_CC }}</span>
        </div>
      </div>
      <div class="status-item">
        <i class="pi pi-wind" />
        <div class="status-data">
          <span class="status-value">{{ player.cleanses }}</span>
          <span class="status-label">{{ LABEL_CLEARS }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import {
  SECTION_BATTLE_STATUS,
  LABEL_DOWNS,
  LABEL_DEATHS,
  LABEL_CC,
  LABEL_CLEARS,
} from '@/constants/eiLabels'

defineProps<{
  player: Player
}>()
</script>

<style scoped lang="css">
.status-section { margin-bottom: 1.5rem; }

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
}

.status-item i { font-size: 1.5rem; color: var(--color-text-secondary); }
.status-item.danger i { color: var(--color-error); }

.status-data { text-align: center; }

.status-value { display: block; font-size: 1.125rem; font-weight: 700; color: var(--color-text); }
.status-item.danger .status-value { color: var(--color-error); }
.status-label { display: block; font-size: 0.7rem; color: var(--color-text-secondary); }
</style>
