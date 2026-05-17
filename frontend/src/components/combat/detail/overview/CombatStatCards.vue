<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <h3 class="text-sm font-semibold text-neutral-text mb-5 flex items-center gap-2">
      <div class="p-1.5 rounded-lg bg-primary/10">
        <i class="pi pi-chart-bar text-primary" />
      </div>
      {{ SECTION_TITLE }}
    </h3>
    <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 xl:grid-cols-10 gap-3">
      <!-- 伤害构成 -->
      <div
        class="card p-3 rounded-xl border-primary/20 bg-gradient-to-br from-primary/5 to-transparent hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 cursor-pointer"
        @click="emit('show-damage-detail')"
      >
        <div class="flex flex-col items-center">
          <DonutChart
            class="mb-2"
            :config="{ size: 48, strokeWidth: 8, radius: 42, trackColor: 'var(--color-border)' }"
            :segments="[
              { color: CHART_COLORS.POWER_DAMAGE, value: agg.total_power_damage },
              { color: CHART_COLORS.CONDI_DAMAGE, value: agg.total_condi_damage + agg.total_breakbar_damage },
            ]"
          >
            <i class="pi pi-chart-pie text-primary text-sm" />
          </DonutChart>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(donut.total) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.DAMAGE_COMPOSITION }}
          </p>
        </div>
      </div>

      <!-- 保护覆盖率 -->
      <div
        class="card p-3 rounded-xl border-info/20 bg-gradient-to-br from-info/5 to-transparent hover:border-info/40 hover:shadow-lg hover:shadow-info/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'protection', STAT_DETAIL_TITLES.PROTECTION)"
      >
        <div class="flex flex-col items-center">
          <div class="relative w-12 h-12 mb-2">
            <svg
              :viewBox="SVG_CONFIG.VIEWBOX"
              class="w-full h-full -rotate-90"
            >
              <circle
                :cx="SVG_CONFIG.CENTER"
                :cy="SVG_CONFIG.CENTER"
                :r="SVG_CONFIG.RADIUS"
                fill="none"
                stroke="var(--color-border)"
                :stroke-width="SVG_CONFIG.STROKE_WIDTH"
              />
              <circle
                :cx="SVG_CONFIG.CENTER"
                :cy="SVG_CONFIG.CENTER"
                :r="SVG_CONFIG.RADIUS"
                fill="none"
                :stroke="CHART_COLORS.PROTECTION_STROKE"
                :stroke-width="SVG_CONFIG.STROKE_WIDTH"
                :stroke-dasharray="SVG_CONFIG.CIRCUMFERENCE"
                :stroke-dashoffset="SVG_CONFIG.CIRCUMFERENCE - (SVG_CONFIG.CIRCUMFERENCE * averages.protection / 100)"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <i class="pi pi-shield text-info text-sm" />
            </div>
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.protection.toFixed(0) }}%
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.PROTECTION }}
          </p>
        </div>
      </div>

      <!-- 稳固覆盖率 -->
      <div
        class="card p-3 rounded-xl border-warning/20 bg-gradient-to-br from-warning/5 to-transparent hover:border-warning/40 hover:shadow-lg hover:shadow-warning/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'stability', STAT_DETAIL_TITLES.STABILITY)"
      >
        <div class="flex flex-col items-center">
          <div class="relative w-12 h-12 mb-2">
            <svg
              :viewBox="SVG_CONFIG.VIEWBOX"
              class="w-full h-full -rotate-90"
            >
              <circle
                :cx="SVG_CONFIG.CENTER"
                :cy="SVG_CONFIG.CENTER"
                :r="SVG_CONFIG.RADIUS"
                fill="none"
                stroke="var(--color-border)"
                :stroke-width="SVG_CONFIG.STROKE_WIDTH"
              />
              <circle
                :cx="SVG_CONFIG.CENTER"
                :cy="SVG_CONFIG.CENTER"
                :r="SVG_CONFIG.RADIUS"
                fill="none"
                :stroke="CHART_COLORS.STABILITY_STROKE"
                :stroke-width="SVG_CONFIG.STROKE_WIDTH"
                :stroke-dasharray="SVG_CONFIG.CIRCUMFERENCE"
                :stroke-dashoffset="SVG_CONFIG.CIRCUMFERENCE - (SVG_CONFIG.CIRCUMFERENCE * averages.stability / 100)"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <i class="pi pi-lock text-warning text-sm" />
            </div>
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.stability.toFixed(0) }}%
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.STABILITY }}
          </p>
        </div>
      </div>

      <!-- 清症总数 -->
      <div
        class="card p-3 rounded-xl border-success/20 bg-gradient-to-br from-success/5 to-transparent hover:border-success/40 hover:shadow-lg hover:shadow-success/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'condition_cleanses', STAT_DETAIL_TITLES.CLEANSES)"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-success/10 mb-2">
            <i class="pi pi-heart text-success text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(agg.total_condition_cleanses) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.CLEANSES }}
          </p>
        </div>
      </div>

      <!-- 削增益总数 -->
      <div
        class="card p-3 rounded-xl border-error/20 bg-gradient-to-br from-error/5 to-transparent hover:border-error/40 hover:shadow-lg hover:shadow-error/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'boon_strips', STAT_DETAIL_TITLES.BOON_STRIPS)"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-error/10 mb-2">
            <i class="pi pi-minus-circle text-error text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(agg.total_boon_strips) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.BOON_STRIPS }}
          </p>
        </div>
      </div>

      <!-- 承伤总量 -->
      <div
        class="card p-3 rounded-xl border-secondary/20 bg-gradient-to-br from-secondary/5 to-transparent hover:border-secondary/40 hover:shadow-lg hover:shadow-secondary/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'damage_taken', STAT_DETAIL_TITLES.DAMAGE_TAKEN)"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-secondary/10 mb-2">
            <i class="pi pi-exclamation-triangle text-secondary text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(agg.total_damage_taken) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.DAMAGE_TAKEN }}
          </p>
        </div>
      </div>

      <!-- 命中率 -->
      <div
        class="card p-3 rounded-xl border-primary/20 bg-gradient-to-br from-primary/5 to-transparent hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'hitRate', STAT_DETAIL_TITLES.HIT_RATE)"
      >
        <div class="flex flex-col items-center">
          <div class="relative w-12 h-12 mb-2">
            <svg
              :viewBox="SVG_CONFIG.VIEWBOX"
              class="w-full h-full -rotate-90"
            >
              <circle
                :cx="SVG_CONFIG.CENTER"
                :cy="SVG_CONFIG.CENTER"
                :r="SVG_CONFIG.RADIUS"
                fill="none"
                stroke="var(--color-border)"
                :stroke-width="SVG_CONFIG.STROKE_WIDTH"
              />
              <circle
                :cx="SVG_CONFIG.CENTER"
                :cy="SVG_CONFIG.CENTER"
                :r="SVG_CONFIG.RADIUS"
                fill="none"
                :stroke="CHART_COLORS.HIT_RATE_STROKE"
                :stroke-width="SVG_CONFIG.STROKE_WIDTH"
                :stroke-dasharray="SVG_CONFIG.CIRCUMFERENCE"
                :stroke-dashoffset="SVG_CONFIG.CIRCUMFERENCE - (SVG_CONFIG.CIRCUMFERENCE * averages.hitRate / 100)"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <i class="pi pi-bolt text-primary text-sm" />
            </div>
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.hitRate.toFixed(1) }}%
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.HIT_RATE }}
          </p>
        </div>
      </div>

      <!-- 击倒控制 -->
      <div
        class="card p-3 rounded-xl border-warning/20 bg-gradient-to-br from-warning/5 to-transparent hover:border-warning/40 hover:shadow-lg hover:shadow-warning/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'control', STAT_DETAIL_TITLES.CONTROL)"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-warning/10 mb-2">
            <i class="pi pi-arrow-down text-warning text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ agg.total_downed || 0 }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.DOWNED }}
          </p>
        </div>
      </div>

      <!-- 技能效率 -->
      <div
        class="card p-3 rounded-xl border-secondary/20 bg-gradient-to-br from-secondary/5 to-transparent hover:border-secondary/40 hover:shadow-lg hover:shadow-secondary/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'efficiency', STAT_DETAIL_TITLES.EFFICIENCY)"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-secondary/10 mb-2">
            <i class="pi pi-cog text-secondary text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.skillCastUptime?.toFixed(0) ?? 0 }}%
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.SKILL_CAST_UPTIME }}
          </p>
        </div>
      </div>

      <!-- 位置协同 -->
      <div
        class="card p-3 rounded-xl border-info/20 bg-gradient-to-br from-info/5 to-transparent hover:border-info/40 hover:shadow-lg hover:shadow-info/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'position', STAT_DETAIL_TITLES.POSITION)"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-info/10 mb-2">
            <i class="pi pi-map-marker text-info text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.stackDist?.toFixed(0) ?? 0 }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ STAT_LABELS.STACK_DISTANCE }}
          </p>
          <p class="text-[10px] text-neutral-text-secondary mt-1">
            {{ STAT_LABELS.COMMANDER_DISTANCE }} {{ averages.distToCom?.toFixed(0) ?? 0 }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import DonutChart from '@/components/common/charts/DonutChart.vue'
import { fmtCompact } from '@/composables/combat/useCombatHelpers'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// === 常量定义 ===
const SECTION_TITLE = t('tactical.stats.title')

const STAT_LABELS = {
  DAMAGE_COMPOSITION: t('tactical.stats.damageComp'),
  PROTECTION: t('tactical.stats.protection'),
  STABILITY: t('tactical.stats.stability'),
  CLEANSES: t('tactical.stats.condiCleanse'),
  BOON_STRIPS: t('tactical.stats.boonStrip'),
  DAMAGE_TAKEN: t('tactical.stats.damageTaken'),
  HIT_RATE: t('tactical.stats.hitRate'),
  DOWNED: t('tactical.stats.downed'),
  SKILL_CAST_UPTIME: t('tactical.stats.castUptime'),
  STACK_DISTANCE: t('tactical.stats.stackDist'),
  COMMANDER_DISTANCE: t('tactical.stats.comDist'),
} as const

const STAT_DETAIL_TITLES = {
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
  VIEWBOX: '0 0 100 100',
  CENTER: 50,
  RADIUS: 42,
  STROKE_WIDTH: 8,
  CIRCUMFERENCE: 264,
} as const

const CHART_COLORS = {
  POWER_DAMAGE: 'var(--color-primary)',
  CONDI_DAMAGE: 'var(--color-success)',
  PROTECTION_STROKE: 'var(--color-info)',
  STABILITY_STROKE: 'var(--color-warning)',
  HIT_RATE_STROKE: 'var(--color-primary)',
} as const

const { agg, averages, donut } = defineProps<{
  agg: EiAnalysisAggregate
  averages: Record<string, number>
  donut: any
}>()

const emit = defineEmits<{
  'show-damage-detail': []
  'open-stat-detail': [type: string, title: string]
}>()
</script>
