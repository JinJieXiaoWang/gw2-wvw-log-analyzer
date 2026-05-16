<template>
  <div class="card p-4 rounded-xl border-neutral-border/50">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-info/10">
          <i class="pi pi-users text-info" />
        </div>{{ SECTION_TITLES.PROFESSION_DISTRIBUTION }}
      </h3>
      <span class="text-xs text-neutral-text-secondary">{{ totalPlayers }} {{ UI_LABELS.PLAYERS_COUNT_UNIT }}{{ UI_LABELS.IN_BATTLE }}</span>
    </div>
    <div class="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-2">
      <div
        v-for="(count, prof) in distribution"
        :key="prof"
        class="flex flex-col items-center p-2 rounded-lg bg-neutral-bg/50 hover:bg-neutral-bg-secondary transition-all"
      >
        <span
          class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-1"
          :style="profStyle(prof)"
        >{{ count }}</span>
        <span
          class="text-[10px] text-center px-1 rounded"
          :style="profStyle(prof)"
        >{{ getProfessionName(prof) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getProfessionColor, getProfessionName } from '@/utils/profession/professionUtils'

const SECTION_TITLES = {
  PROFESSION_DISTRIBUTION: '职业分布',
} as const

const UI_LABELS = {
  PLAYERS_COUNT_UNIT: '人',
  IN_BATTLE: '参战',
} as const

defineProps<{
  distribution: Record<string, number>
  totalPlayers: number
}>()

function profStyle(prof: string) {
  const c = getProfessionColor(prof)
  return { backgroundColor: c + '20', color: c }
}
</script>
