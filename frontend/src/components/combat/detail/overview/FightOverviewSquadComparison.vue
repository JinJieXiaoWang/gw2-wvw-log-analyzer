<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <h3 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2">
      <div class="p-1.5 rounded-lg bg-primary/10">
        <i class="pi pi-chart-bar text-primary" />
      </div>{{ SECTION_TITLES.SQUAD_COMPARISON }}
    </h3>
    <div class="space-y-3">
      <div
        v-for="g in groups"
        :key="g.id"
        class="flex items-center gap-4"
      >
        <span
          class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
          :style="{ backgroundColor: groupColor(g.id) }"
        >{{ g.id }}</span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs text-neutral-text-secondary">{{ SQUAD_LABELS.SQUAD_PREFIX }} {{ g.id }} {{ SQUAD_LABELS.SEPARATOR }} {{ g.players.length }}{{ UI_LABELS.PLAYERS_COUNT_UNIT }}</span>
            <span class="text-xs font-semibold text-primary">{{ fmtCompact(g.total_damage) }}</span>
          </div>
          <div class="h-2 bg-neutral-bg rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :style="teamBarStyle(g)"
            />
          </div>
        </div>
        <div class="flex items-center gap-3 text-xs flex-shrink-0">
          <div class="text-center">
            <span class="block font-semibold text-neutral-text">{{ fmtCompact(g.avg_dps) }}</span><span class="text-neutral-text-secondary">{{ UI_LABELS.AVG_DPS }}</span>
          </div>
          <div class="text-center">
            <span class="block font-semibold text-error">{{ g.total_dead }}</span><span class="text-neutral-text-secondary">{{ UI_LABELS.DEATHS }}</span>
          </div>
          <div class="text-center">
            <span class="block font-semibold text-warning">{{ g.total_downed }}</span><span class="text-neutral-text-secondary">{{ UI_LABELS.DOWNED }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EiAnalysisGroup } from '@/services/ei/eiAnalysisService'
import { groupColor } from '@/utils/combat/combatFormatters'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const SECTION_TITLES = {
  SQUAD_COMPARISON: t('tactical.overview.squadCompare'),
} as const

const SQUAD_LABELS = {
  SQUAD_PREFIX: t('tactical.overview.squadPrefix'),
  SEPARATOR: '·',
} as const

const UI_LABELS = {
  AVG_DPS: t('tactical.overview.avgDps'),
  DEATHS: t('tactical.overview.death'),
  DOWNED: t('tactical.overview.downed'),
  PLAYERS_COUNT_UNIT: t('tactical.units.person'),
} as const

const TEAM_BAR_CONFIG = {
  SCALE_FACTOR: 50,
  MAX_PERCENTAGE: 100,
} as const

const props = defineProps<{
  groups: EiAnalysisGroup[]
}>()

function teamBarStyle(g: EiAnalysisGroup) {
  const totalDmg = props.groups.reduce((s, x) => s + x.total_damage, 0)
  const avgDmg = totalDmg / Math.max(props.groups.length, 1)
  const width = Math.min((g.total_damage / Math.max(avgDmg, 1)) * TEAM_BAR_CONFIG.SCALE_FACTOR, TEAM_BAR_CONFIG.MAX_PERCENTAGE)
  return { width: width + '%', backgroundColor: groupColor(g.id) }
}
</script>
