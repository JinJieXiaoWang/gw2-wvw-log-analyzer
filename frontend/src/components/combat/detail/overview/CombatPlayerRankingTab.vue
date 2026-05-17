<script setup lang="ts">
import type { EiAnalysisResponse, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import Tag from 'primevue/tag'
import { fmtCompact } from '@/composables/combat/useCombatHelpers'
import { useProfessionHelpers } from '@/composables/useProfession'
import PlayerRankingTable from '@/components/combat/ranking/PlayerRankingTable.vue'
import SquadCompositionPanel from '@/components/combat/ranking/SquadCompositionPanel.vue'
import { useI18n } from 'vue-i18n'

const { getProfessionName, getProfessionIconUrl } = useProfessionHelpers()

const props = defineProps<{
  players: EiAnalysisPlayer[]
  sortedPlayerList: EiAnalysisPlayer[]
  groups: any[]
  commanders: EiAnalysisPlayer[]
  ungroupedPlayers: EiAnalysisPlayer[]
  summary: EiAnalysisResponse | null
}>()

const { t } = useI18n()

const emit = defineEmits<{
  'row-click': [event: any]
  'open-player-dialog': [player: EiAnalysisPlayer]
}>()
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center gap-3">
      <div class="p-2 rounded-lg bg-yellow-500/10">
        <i class="pi pi-trophy text-yellow-500" />
      </div>
      <h3 class="text-lg font-semibold text-neutral-text">
        {{ t('tactical.ranking.title') }}
      </h3>
      <Tag
        :value="players.length + t('tactical.units.person')"
        severity="info"
        class="text-xs"
      />
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-5 gap-5">
      <div class="xl:col-span-3">
        <PlayerRankingTable
          :sorted-player-list="sortedPlayerList"
          @row-click="emit('row-click', $event)"
        />
      </div>
      <div class="xl:col-span-2">
        <SquadCompositionPanel
          :groups="groups"
          :commanders="commanders"
          :ungrouped-players="ungroupedPlayers"
          @open-player-dialog="emit('open-player-dialog', $event)"
        />
      </div>
    </div>

    <div
      v-if="summary?.enemy_players?.length"
      class="card p-4 rounded-xl border-error/20 bg-error/5"
    >
      <h4 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
        <div class="p-1 rounded bg-error/20">
          <i class="pi pi-exclamation-triangle text-error text-xs" />
        </div>
        {{ t('tactical.ranking.enemyTarget') }} ({{ summary.enemy_players.length }})
      </h4>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="p in summary.enemy_players.slice(0, 10)"
          :key="p.id"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-error/10 border border-error/20"
        >
          <img
            :src="getProfessionIconUrl(p.profession)"
            class="w-6 h-6 rounded-full border border-error/30"
            :alt="getProfessionName(p.profession)"
          >
          <span class="text-xs text-neutral-text">{{ p.character_name || t('tactical.ranking.unknown') }}</span>
          <span class="text-[10px] text-error font-semibold">{{ fmtCompact(p.damage) }}</span>
        </div>
        <div
          v-if="(summary.enemy_players.length || 0) > 10"
          class="flex items-center px-3 py-1.5 text-xs text-neutral-text-secondary"
        >
          +{{ (summary.enemy_players.length || 0) - 10 }} {{ t('tactical.ranking.more') }}
        </div>
      </div>
    </div>
  </div>
</template>
