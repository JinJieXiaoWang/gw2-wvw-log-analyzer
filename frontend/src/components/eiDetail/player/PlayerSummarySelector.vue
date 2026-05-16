<template>
  <div class="player-selector card">
    <div class="selector-header">
      <h3 class="selector-title">
        <i class="pi pi-user" />
        玩家详细统计
      </h3>
    </div>
    <div class="selector-list">
      <button
        v-for="player in players"
        :key="player.instanceID"
        class="player-btn"
        :class="{ active: selectedId === player.instanceID }"
        @click="selectPlayer(player.instanceID)"
      >
        <img
          :src="getProfIcon(player.profession)"
          class="btn-avatar"
          alt=""
        >
        <div class="btn-info">
          <span class="btn-name">{{ player.name }}</span>
          <span class="btn-prof">{{ getProfessionName(player.profession) }}</span>
        </div>
        <span class="btn-dps">{{ formatDamage(player.dps) }} DPS</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'
import { getProfessionIconUrl, getProfessionName } from '@/utils/profession/professionUtils'

interface Props {
  players: Player[]
  selectedId: number | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select-player', id: number): void
}>()

function selectPlayer(id: number) {
  emit('select-player', id)
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.player-selector {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.selector-header {
  padding: 1rem 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
}

.selector-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.selector-title i {
  color: var(--color-primary);
}

.selector-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
  padding: 1.25rem;
  max-height: 280px;
  overflow-y: auto;
}

.player-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.player-btn:hover {
  border-color: var(--color-primary-alpha-30);
  background-color: var(--color-card-hover);
}

.player-btn.active {
  border-color: var(--color-primary);
  background-color: var(--color-primary-alpha-10);
  box-shadow: 0 0 10px var(--color-primary-alpha-30);
}

.btn-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.btn-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  flex: 1;
  min-width: 0;
}

.btn-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-prof {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.btn-dps {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-accent);
  white-space: nowrap;
}
</style>
