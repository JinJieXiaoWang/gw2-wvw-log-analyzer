<template>
  <Card class="border-none bg-surface-100/50">
    <template #content>
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-full flex-shrink-0 overflow-hidden" :style="{ backgroundColor: color + '30' }">
          <img :src="getProfessionIconUrl(player.profession)" :alt="getProfessionName(player.profession)" class="w-full h-full object-cover" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <h3 class="text-lg font-bold text-primary">{{ player.character_name || player.account }}</h3>
            <Badge v-if="player.score_grade" :severity="getScoreSeverity(player.score_grade)" class="text-xs">{{ player.score_grade }}</Badge>
          </div>
          <p v-if="player.account && player.character_name" class="text-sm text-neutral-text-secondary mb-1">{{ player.account }}</p>
          <p class="text-sm text-neutral-text-secondary flex items-center gap-1"><i class="pi pi-users text-xs" />{{ getProfessionName(player.profession) }}</p>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div class="text-center p-2 rounded-lg bg-surface-200/50"><p class="text-xl font-bold text-primary">{{ fmtCompact(player.damage) }}</p><p class="text-xs text-neutral-text-secondary mt-1">总伤害</p></div>
          <div class="text-center p-2 rounded-lg bg-surface-200/50"><p class="text-xl font-bold text-primary">{{ fmtCompact(player.dps) }}</p><p class="text-xs text-neutral-text-secondary mt-1">DPS</p></div>
          <div class="text-center p-2 rounded-lg bg-surface-200/50"><p class="text-xl font-bold" :style="{ color }">{{ player.score_grade || '-' }}</p><p class="text-xs text-neutral-text-secondary mt-1">评分</p></div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from 'primevue/card'
import Badge from 'primevue/badge'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getProfessionColor, getProfessionName, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import { getScoreSeverity } from '@/utils/combat/playerDetailHelpers'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

const props = defineProps<{ player: EiAnalysisPlayer }>()
const color = getProfessionColor(props.player.profession) || '#64748b'
</script>
