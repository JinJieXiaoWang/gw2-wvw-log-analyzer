<template>
  <div class="card-header">
    <div class="player-info-header">
      <img
        :src="getProfIcon(player.profession)"
        class="player-avatar-lg"
      >
      <div class="player-main-info">
        <h3 class="player-name-lg">
          {{ player.name }}
        </h3>
        <span
          class="profession-tag"
          :style="{ backgroundColor: getProfessionColor(player.profession) }"
        >
          {{ getProfessionName(player.profession) }}
        </span>
      </div>
    </div>
    <button
      class="close-btn"
      @click="$emit('close')"
    >
      <i class="pi pi-times" />
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionColor, getProfessionIconUrl, getProfessionName } from '@/utils/profession/professionUtils'
import { PLAYER_AVATAR_LARGE_SIZE } from '@/constants/dimensions'

defineProps<{
  player: Player
}>()

defineEmits(['close'])

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
}

.player-info-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-avatar-lg {
  width: v-bind(PLAYER_AVATAR_LARGE_SIZE);
  height: v-bind(PLAYER_AVATAR_LARGE_SIZE);
  border-radius: 50%;
}

.player-main-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.player-name-lg {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.profession-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
  width: fit-content;
}

.close-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: var(--color-border);
}
</style>
