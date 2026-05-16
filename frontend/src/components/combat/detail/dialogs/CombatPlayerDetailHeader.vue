<template>
  <div class="flex items-center gap-4 pb-4 border-b border-neutral-border">
    <img
      :src="getProfessionIconUrl(player.profession)"
      class="w-12 h-12 rounded-full"
    >
    <div>
      <p class="text-lg font-bold text-neutral-text">
        {{ player.character_name || player.account }}
      </p>
      <p
        v-if="player.account && player.character_name"
        class="text-sm text-neutral-text-secondary"
      >
        {{ player.account }}
      </p>
      <p class="text-sm text-neutral-text-secondary">
        {{ getProfessionName(player.profession) }}
      </p>
    </div>
    <div class="ml-auto flex gap-3 text-sm">
      <div class="text-center">
        <p class="font-bold text-primary">
          {{ fmtCompact(player.damage) }}
        </p>
        <p class="text-xs text-neutral-text-secondary">
          {{ LABELS.TOTAL_DAMAGE }}
        </p>
      </div>
      <div class="text-center">
        <p class="font-bold text-primary">
          {{ fmtCompact(player.dps) }}
        </p>
        <p class="text-xs text-neutral-text-secondary">
          {{ LABELS.DPS }}
        </p>
      </div>
      <div class="text-center">
        <p class="font-bold text-status-success">
          {{ player.score_grade || '-' }}
        </p>
        <p class="text-xs text-neutral-text-secondary">
          {{ LABELS.GRADE }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { fmtCompact, getProfessionIconUrl, getProfessionName } from '@/composables/combat/useCombatHelpers'

const LABELS = {
  TOTAL_DAMAGE: '总伤害',
  DPS: 'DPS',
  GRADE: '评分',
} as const

defineProps<{
  player: EiAnalysisPlayer
}>()
</script>
