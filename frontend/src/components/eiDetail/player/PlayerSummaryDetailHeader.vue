<template>
  <div class="detail-header">
    <div class="detail-player-info">
      <img
        :src="getProfIcon(player.profession)"
        class="detail-avatar"
        alt=""
      >
      <div>
        <h3 class="detail-name">
          {{ player.name }}
        </h3>
        <span
          class="detail-prof-badge"
          :style="{ backgroundColor: getProfessionColor(player.profession) }"
        >
          {{ getProfessionName(player.profession) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionColor, getProfessionIconUrl, getProfessionName } from '@/utils/profession/professionUtils'

interface Props {
  player: Player
}

defineProps<Props>()

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.detail-header {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.detail-player-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.detail-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
}

.detail-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
}

.detail-prof-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
}
</style>
