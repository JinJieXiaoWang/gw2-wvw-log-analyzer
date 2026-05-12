<template>
  <div class="actor-selector grid grid-cols-[1fr 1fr] max-md:grid-cols-1 gap-4 mb-4">
    <!-- 目标选择 -->
    <div class="selector-section bg-neutral-card rounded-xl p-4">
      <div class="selector-label flex items-center gap-2 text-sm font-semibold text-neutral-text mb-3">
        <i class="pi pi-crosshair" />
        <span>目标</span>
      </div>
      <div class="actor-list flex flex-wrap gap-2 max-h-40 overflow-y-auto">
        <button
          class="actor-btn all flex items-center gap-1.5 p-[0.375rem 0.625rem] rounded-md bg-neutral-bg text-neutral-text-secondary cursor-pointer text-[0.8125rem] font-medium"
          :class="{ active: selectedTargetId === null }"
          @click="$emit('select-target', null)"
        >
          <span class="actor-name max-w-[120px] overflow-hidden whitespace-nowrap">全部目标</span>
        </button>
        <button
          v-for="target in targets"
          :key="target.instanceID"
          class="actor-btn flex items-center gap-1.5 p-[0.375rem 0.625rem] rounded-md bg-neutral-bg text-neutral-text-secondary cursor-pointer text-[0.8125rem]"
          :class="{ active: selectedTargetId === target.instanceID, 'opacity-60 line-through': target.finalHealth === 0 }"
          @click="$emit('select-target', target.instanceID)"
        >
          <img
            v-if="target.icon"
            :src="target.icon"
            class="actor-icon w-5 h-5 rounded"
            alt=""
          >
          <span class="actor-name max-w-[120px] overflow-hidden whitespace-nowrap">{{ target.name }}</span>
          <span
            v-if="target.finalHealth === 0"
            class="actor-status text-[0.7rem] p-[0.125rem 0.375rem] bg-red-500/[0.2] text-red-500 rounded-full"
          >已击杀</span>
        </button>
      </div>
    </div>

    <!-- 玩家选择 -->
    <div class="selector-section bg-neutral-card rounded-xl p-4">
      <div class="selector-label flex items-center gap-2 text-sm font-semibold text-neutral-text mb-3">
        <i class="pi pi-users" />
        <span>玩家</span>
      </div>
      <div class="actor-list flex flex-wrap gap-2 max-h-40 overflow-y-auto">
        <button
          class="actor-btn all flex items-center gap-1.5 p-[0.375rem 0.625rem] rounded-md bg-neutral-bg text-neutral-text-secondary cursor-pointer text-[0.8125rem] font-medium"
          :class="{ active: selectedPlayerId === null }"
          @click="$emit('select-player', null)"
        >
          <span class="actor-name max-w-[120px] overflow-hidden whitespace-nowrap">全部玩家</span>
        </button>
        <button
          v-for="player in players"
          :key="player.instanceID"
          class="actor-btn flex items-center gap-1.5 p-[0.375rem 0.625rem] rounded-md bg-neutral-bg text-neutral-text-secondary cursor-pointer text-[0.8125rem]"
          :class="{ active: selectedPlayerId === player.instanceID }"
          @click="$emit('select-player', player.instanceID)"
        >
          <img
            :src="getProfIcon(player.profession)"
            class="actor-icon w-5 h-5 rounded"
            alt=""
          >
          <span class="actor-name max-w-[120px] overflow-hidden whitespace-nowrap">{{ player.name }}</span>
          <span
            class="profession-dot w-2 h-2 rounded-full"
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
.selector-label i {
  color: var(--color-accent);
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
</style>
