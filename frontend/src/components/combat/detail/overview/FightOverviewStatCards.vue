<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
      <div class="p-1.5 rounded-lg bg-primary/10">
        <i class="pi pi-chart-bar text-primary" />
      </div>{{ SECTION_TITLES.COMBAT_STATS }}
    </h3>
    <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 xl:grid-cols-10 gap-3">
      <div
        v-for="s in statCards"
        :key="s.key"
        class="card p-3 rounded-xl border hover:shadow-lg transition-all cursor-pointer flex flex-col items-center"
        :class="[s.border, s.bg]"
        @click="emit('open-stat-detail', s.category, s.dialogTitle)"
      >
        <template v-if="s.type === 'multi-ring'">
          <div class="relative w-12 h-12 mb-2">
            <svg
              viewBox="0 0 100 100"
              class="w-full h-full -rotate-90"
            >
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="var(--color-border)"
                stroke-width="8"
              />
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                :stroke="CHART_COLORS.PRIMARY"
                stroke-width="8"
                :stroke-dasharray="donut.pd"
              />
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                :stroke="CHART_COLORS.SUCCESS"
                stroke-width="8"
                :stroke-dasharray="donut.cd"
                :stroke-dashoffset="donut.co"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <i :class="s.icon + ' text-primary text-sm'" />
            </div>
          </div>
        </template>
        <template v-else-if="s.type === 'ring'">
          <div class="relative w-12 h-12 mb-2">
            <svg
              viewBox="0 0 100 100"
              class="w-full h-full -rotate-90"
            >
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                stroke="var(--color-border)"
                stroke-width="8"
              />
              <circle
                cx="50"
                cy="50"
                r="42"
                fill="none"
                :stroke="s.ringColor"
                stroke-width="8"
                :stroke-dasharray="SVG_CONFIG.CIRCUMFERENCE"
                :stroke-dashoffset="SVG_CONFIG.CIRCUMFERENCE - (SVG_CONFIG.CIRCUMFERENCE * s.percent / 100)"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <i :class="s.icon + ' text-' + s.color + ' text-sm'" />
            </div>
          </div>
        </template>
        <template v-else>
          <div
            class="p-2 rounded-lg mb-2"
            :class="'bg-' + s.color + '/10'"
          >
            <i :class="s.icon + ' text-' + s.color + ' text-lg'" />
          </div>
        </template>
        <p class="text-lg font-bold text-neutral-text">
          {{ s.value }}
        </p>
        <p class="text-xs text-neutral-text-secondary">
          {{ s.label }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DonutData, StatAverages } from '@/composables/combat/useCombatLogDetail'
import type { EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import { type StatCategory } from '@/utils/combat/combatStats'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const SECTION_TITLES = {
  COMBAT_STATS: t('tactical.stats.title'),
} as const

const STAT_LABELS = {
  DAMAGE_OUTPUT: t('tactical.stats.damageComp'),
  PROTECTION: t('tactical.stats.protection'),
  STABILITY: t('tactical.stats.stability'),
  CLEANSES: t('tactical.stats.condiCleanse'),
  BOON_STRIPS: t('tactical.stats.boonStrip'),
  DAMAGE_TAKEN: t('tactical.stats.damageTaken'),
  HIT_RATE: t('tactical.stats.hitRate'),
  CONTROL: t('tactical.stats.downed'),
  EFFICIENCY: t('tactical.stats.castUptime'),
  POSITION: t('tactical.stats.stackDist'),
} as const

const DIALOG_TITLES = {
  DAMAGE_OUTPUT: t('tactical.stats.damageComp'),
  PROTECTION: t('tactical.stats.protection'),
  STABILITY: t('tactical.stats.stability'),
  CLEANSES: t('tactical.stats.condiCleanse'),
  BOON_STRIPS: t('tactical.stats.boonStrip'),
  DAMAGE_TAKEN: t('tactical.stats.damageTaken'),
  HIT_RATE: t('tactical.stats.hitRate'),
  CONTROL: t('tactical.stats.downed'),
  EFFICIENCY: t('tactical.stats.castUptime'),
  POSITION: t('tactical.stats.stackDist'),
} as const

const SVG_CONFIG = {
  CIRCUMFERENCE: 264,
} as const

const CHART_COLORS = {
  PRIMARY: 'var(--color-primary)',
  SUCCESS: 'var(--color-success)',
  INFO: 'var(--color-info)',
  WARNING: 'var(--color-warning)',
} as const

const props = defineProps<{
  donut: DonutData
  statAverages: StatAverages
  agg: EiAnalysisAggregate
}>()

const emit = defineEmits<{
  'open-stat-detail': [type: StatCategory, title: string]
}>()

const statCards = computed(() => {
  const sa = props.statAverages
  const d = props.donut
  const agg = props.agg
  return [
    { type: 'multi-ring' as const, key: 'damage', label: STAT_LABELS.DAMAGE_OUTPUT, category: 'damage_output' as StatCategory, dialogTitle: DIALOG_TITLES.DAMAGE_OUTPUT, value: fmtCompact(d.total), icon: 'pi pi-chart-pie', color: 'primary', border: 'border-primary/20', bg: 'bg-gradient-to-br from-primary/5 to-transparent' },
    { type: 'ring' as const, key: 'protection', label: STAT_LABELS.PROTECTION, category: 'protection' as StatCategory, dialogTitle: DIALOG_TITLES.PROTECTION, value: sa.protection.toFixed(0) + '%', icon: 'pi pi-shield', color: 'info', ringColor: CHART_COLORS.INFO, percent: sa.protection, border: 'border-info/20', bg: 'bg-gradient-to-br from-info/5 to-transparent' },
    { type: 'ring' as const, key: 'stability', label: STAT_LABELS.STABILITY, category: 'stability' as StatCategory, dialogTitle: DIALOG_TITLES.STABILITY, value: sa.stability.toFixed(0) + '%', icon: 'pi pi-lock', color: 'warning', ringColor: CHART_COLORS.WARNING, percent: sa.stability, border: 'border-warning/20', bg: 'bg-gradient-to-br from-warning/5 to-transparent' },
    { type: 'icon' as const, key: 'cleanses', label: STAT_LABELS.CLEANSES, category: 'condition_cleanses' as StatCategory, dialogTitle: DIALOG_TITLES.CLEANSES, value: fmtCompact(agg.total_condition_cleanses), icon: 'pi pi-heart', color: 'success', border: 'border-success/20', bg: 'bg-gradient-to-br from-success/5 to-transparent' },
    { type: 'icon' as const, key: 'strips', label: STAT_LABELS.BOON_STRIPS, category: 'boon_strips' as StatCategory, dialogTitle: DIALOG_TITLES.BOON_STRIPS, value: fmtCompact(agg.total_boon_strips), icon: 'pi pi-minus-circle', color: 'error', border: 'border-error/20', bg: 'bg-gradient-to-br from-error/5 to-transparent' },
    { type: 'icon' as const, key: 'taken', label: STAT_LABELS.DAMAGE_TAKEN, category: 'damage_taken' as StatCategory, dialogTitle: DIALOG_TITLES.DAMAGE_TAKEN, value: fmtCompact(agg.total_damage_taken), icon: 'pi pi-exclamation-triangle', color: 'secondary', border: 'border-secondary/20', bg: 'bg-gradient-to-br from-secondary/5 to-transparent' },
    { type: 'ring' as const, key: 'hitRate', label: STAT_LABELS.HIT_RATE, category: 'hitRate' as StatCategory, dialogTitle: DIALOG_TITLES.HIT_RATE, value: sa.hitRate.toFixed(1) + '%', icon: 'pi pi-bolt', color: 'primary', ringColor: CHART_COLORS.PRIMARY, percent: sa.hitRate, border: 'border-primary/20', bg: 'bg-gradient-to-br from-primary/5 to-transparent' },
    { type: 'icon' as const, key: 'control', label: STAT_LABELS.CONTROL, category: 'control' as StatCategory, dialogTitle: DIALOG_TITLES.CONTROL, value: String(agg.total_downed || 0), icon: 'pi pi-arrow-down', color: 'warning', border: 'border-warning/20', bg: 'bg-gradient-to-br from-warning/5 to-transparent' },
    { type: 'icon' as const, key: 'efficiency', label: STAT_LABELS.EFFICIENCY, category: 'efficiency' as StatCategory, dialogTitle: DIALOG_TITLES.EFFICIENCY, value: (sa.skillCastUptime?.toFixed(0) ?? '0') + '%', icon: 'pi pi-cog', color: 'secondary', border: 'border-secondary/20', bg: 'bg-gradient-to-br from-secondary/5 to-transparent' },
    { type: 'icon' as const, key: 'position', label: STAT_LABELS.POSITION, category: 'position' as StatCategory, dialogTitle: DIALOG_TITLES.POSITION, value: sa.stackDist?.toFixed(0) ?? '0', icon: 'pi pi-map-marker', color: 'info', border: 'border-info/20', bg: 'bg-gradient-to-br from-info/5 to-transparent' },
  ]
})
</script>
