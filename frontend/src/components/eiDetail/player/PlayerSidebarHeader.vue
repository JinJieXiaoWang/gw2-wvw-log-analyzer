<template>
  <div class="sidebar-header">
    <div class="header-left">
      <div class="player-avatar">
        <img
          :src="getProfIcon(player.profession)"
          :alt="player.profession"
        >
      </div>
      <div class="player-info">
        <div class="player-name">
          {{ player.name }}
          <span
            v-if="player.hasCommanderTag"
            class="commander-badge"
          ><i class="pi pi-star-fill" /></span>
        </div>
        <div class="player-account">
          {{ player.account }}
        </div>
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
import type { Player } from '@/types/eliteInsights';
import { getProfessionIconUrl } from '@/utils/profession/professionUtils';

interface Props {
  player: Player
}

defineProps<Props>()

defineEmits<{
  (e: 'close'): void
}>()

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: linear-gradient(180deg, var(--color-card) 0%, rgba(40,40,40,1) 100%);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.player-avatar {
  width: 56px;
  height: 56px;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  padding: 3px;
  flex-shrink: 0;
}

.player-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
}

.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.commander-badge {
  color: var(--color-accent);
  font-size: 0.875rem;
}

.player-account {
  font-size: 0.75rem;
  color: var(--color-text-disabled);
  margin-top: 0.25rem;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: var(--color-border);
  color: var(--color-text);
}
</style>
