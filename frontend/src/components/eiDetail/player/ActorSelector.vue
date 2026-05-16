<template>
  <div class="actor-selector">
    <!-- 目标选择 -->
    <div class="selector-section">
      <div class="selector-label">
        <i class="pi pi-crosshair" />
        <span>目标</span>
      </div>
      <div class="actor-list">
        <button
          class="actor-btn all"
          :class="{ active: selectedTargetId === null }"
          @click="$emit('select-target', null)"
        >
          <span class="actor-name">全部目标</span>
        </button>
        <button
          v-for="target in targets"
          :key="target.instanceID"
          class="actor-btn"
          :class="{ active: selectedTargetId === target.instanceID, dead: target.finalHealth === 0 }"
          @click="$emit('select-target', target.instanceID)"
        >
          <img
            v-if="target.icon"
            :src="target.icon"
            class="actor-icon"
            alt=""
          >
          <span class="actor-name">{{ target.name }}</span>
          <span
            v-if="target.finalHealth === 0"
            class="actor-status"
          >已击杀</span>
        </button>
      </div>
    </div>

    <!-- 玩家选择 -->
    <div class="selector-section">
      <div class="selector-label">
        <i class="pi pi-users" />
        <span>玩家</span>
      </div>
      <div class="actor-list">
        <button
          class="actor-btn all"
          :class="{ active: selectedPlayerId === null }"
          @click="$emit('select-player', null)"
        >
          <span class="actor-name">全部玩家</span>
        </button>
        <button
          v-for="player in players"
          :key="player.instanceID"
          class="actor-btn"
          :class="{ active: selectedPlayerId === player.instanceID }"
          @click="$emit('select-player', player.instanceID)"
        >
          <img
            :src="getProfIcon(player.profession)"
            class="actor-icon"
            alt=""
          >
          <span class="actor-name">{{ player.name }}</span>
          <span
            class="profession-dot"
            :style="{ backgroundColor: getProfessionColor(player.profession) }"
          />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player, Target } from '@/types/eliteInsights'
import { getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'

interface Props {
  players: Player[]
  targets: Target[]
  selectedPlayerId: number | null
  selectedTargetId: number | null
}

defineProps<Props>()

defineEmits<{
  (e: 'select-player', id: number | null): void
  (e: 'select-target', id: number | null): void
}>()

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.actor-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.selector-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1rem;
}

.selector-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.75rem;
}

.selector-label i {
  color: var(--color-accent);
}

.actor-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-height: 160px;
  overflow-y: auto;
}

.actor-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-bg);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8125rem;
}

.actor-btn:hover {
  border-color: var(--color-primary-alpha-30);
  background-color: var(--color-card-hover);
}

.actor-btn.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 0 10px var(--color-primary-alpha-30);
}

.actor-btn.all {
  font-weight: 500;
}

.actor-btn.dead {
  opacity: 0.6;
  text-decoration: line-through;
}

.actor-icon {
  width: 20px;
  height: 20px;
  border-radius: 0.25rem;
}

.actor-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actor-status {
  font-size: 0.7rem;
  padding: 0.125rem 0.375rem;
  background-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-radius: 9999px;
}

.profession-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

@media (max-width: 768px) {
  .actor-selector {
    grid-template-columns: 1fr;
  }
}
</style>
