<template>
  <div class="weapons-section">
    <h4 class="section-title">
      {{ SECTION_WEAPON_CONFIG }}
    </h4>
    <div class="weapons-info">
      <span class="weapons-text">{{ player.weapons?.join(' / ') || LABEL_WEAPONS_NOT_RECORDED }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import {
  SECTION_WEAPON_CONFIG,
  LABEL_WEAPONS_NOT_RECORDED,
} from '@/constants/eiLabels'

defineProps<{
  player: Player
}>()
</script>

<style scoped lang="css">
.weapons-section { margin-bottom: 1.5rem; }

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem 0;
}

.weapons-info {
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
}

.weapons-text { font-size: 0.875rem; color: var(--color-text); }
</style>
