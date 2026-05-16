<template>
  <div class="player-detail-card">
    <PlayerStatsDetailHeader :player="player" @close="$emit('close')" />

    <div class="card-content">
      <PlayerStatsOverview :player="player" />
      <PlayerStatsBattleDetails :player="player" />
      <PlayerStatsBattleStatus :player="player" />
      <PlayerStatsWeapons :player="player" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import PlayerStatsDetailHeader from './PlayerStatsDetailHeader.vue'
import PlayerStatsOverview from './PlayerStatsOverview.vue'
import PlayerStatsBattleDetails from './PlayerStatsBattleDetails.vue'
import PlayerStatsBattleStatus from './PlayerStatsBattleStatus.vue'
import PlayerStatsWeapons from './PlayerStatsWeapons.vue'

defineProps<{
  player: Player
}>()

defineEmits(['close'])
</script>

<style scoped lang="css">
.player-detail-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.card-content { padding: 1.25rem; }
</style>
