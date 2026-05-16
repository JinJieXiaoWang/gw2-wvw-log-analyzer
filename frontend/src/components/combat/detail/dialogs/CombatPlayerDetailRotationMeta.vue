<template>
  <!-- 武器配置 -->
  <div
    v-if="weapons.length"
    class="pb-4 border-b border-neutral-border"
  >
    <h4 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
      <i class="pi pi-wrench text-primary" /> {{ LABELS.WEAPON_SETUP }}
    </h4>
    <div class="flex items-center gap-3 flex-wrap">
      <div
        v-for="(w, idx) in weapons.filter((x: string) => x && x !== UNKNOWN_FILTER).slice(0, MAX_DISPLAY_SLOTS)"
        :key="idx"
        class="px-2 py-1 rounded bg-neutral-bg text-xs text-neutral-text"
      >
        {{ WEAPON_NAME_MAP[w] || w }}
      </div>
    </div>
  </div>

  <!-- 食物/扳手 -->
  <div
    v-if="consumables.food?.length || consumables.utility?.length"
    class="pb-4 border-b border-neutral-border"
  >
    <h4 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
      <i class="pi pi-sparkles text-status-success" /> {{ LABELS.CONSUMABLES }}
    </h4>
    <div class="flex flex-wrap gap-2">
      <div
        v-for="(f, idx) in consumables.food"
        :key="`food-${idx}`"
        class="flex items-center gap-2 px-2 py-1 rounded bg-status-success/10 text-xs text-neutral-text"
      >
        <img
          v-if="f.icon"
          :src="f.icon"
          class="w-5 h-5 rounded"
        >
        <span>{{ f.name || FALLBACKS.UNKNOWN_FOOD }}</span>
      </div>
      <div
        v-for="(u, idx) in consumables.utility"
        :key="`util-${idx}`"
        class="flex items-center gap-2 px-2 py-1 rounded bg-primary/10 text-xs text-neutral-text"
      >
        <img
          v-if="u.icon"
          :src="u.icon"
          class="w-5 h-5 rounded"
        >
        <span>{{ u.name || FALLBACKS.UNKNOWN_UTILITY }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { WEAPON_NAME_MAP } from '@/config/combatConstants'

interface ConsumableItem {
  icon?: string
  name?: string
}

const LABELS = {
  WEAPON_SETUP: '武器配置',
  CONSUMABLES: '食物 / 扳手',
} as const

const FALLBACKS = {
  UNKNOWN_FOOD: '未知食物',
  UNKNOWN_UTILITY: '未知扳手',
} as const

const UNKNOWN_FILTER = 'Unknown'
const MAX_DISPLAY_SLOTS = 4

defineProps<{
  weapons: string[]
  consumables: {
    food?: ConsumableItem[]
    utility?: ConsumableItem[]
  }
}>()
</script>
