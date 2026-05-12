<script setup lang="ts">
/**
 * 战斗 KPI 卡片组件
 * 功能：展示战斗概览的核心指标
 * 更新：2026-05-11
 */

import { computed } from 'vue'
import type { EiAnalysisAggregate } from '@/services/ei/eiAnalysisService'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'

const props = defineProps<{
  agg: EiAnalysisAggregate
}>()

const kpiList = computed(() => {
  const maxDamage = 5000000
  const maxDowned = 100
  const maxDeaths = 50
  const maxDps = 50000
  const agg = props.agg

  return [
    {
      icon: 'pi pi-bolt',
      label: '总伤害',
      value: fmtCompact(agg.total_damage),
      color: 'text-primary',
      bg: 'from-primary/20 to-primary/5',
      barColor: 'bg-primary',
      unit: '',
      percent: Math.min((agg.total_damage / maxDamage) * 100, 100)
    },
    {
      icon: 'pi pi-shield',
      label: '总承伤',
      value: fmtCompact(agg.total_damage_taken),
      color: 'text-secondary',
      bg: 'from-secondary/20 to-secondary/5',
      barColor: 'bg-secondary',
      unit: '',
      percent: Math.min((agg.total_damage_taken / maxDamage) * 100, 100)
    },
    {
      icon: 'pi pi-star',
      label: '击杀',
      value: String(agg.total_kills || 0),
      color: 'text-success',
      bg: 'from-success/20 to-success/5',
      barColor: 'bg-success',
      unit: '次',
      percent: Math.min((agg.total_kills / maxDeaths) * 100, 100)
    },
    {
      icon: 'pi pi-times-circle',
      label: '死亡',
      value: String(agg.total_deaths || 0),
      color: 'text-error',
      bg: 'from-error/20 to-error/5',
      barColor: 'bg-error',
      unit: '次',
      percent: Math.min((agg.total_deaths / maxDeaths) * 100, 100)
    },
    {
      icon: 'pi pi-arrow-down',
      label: '击倒',
      value: String(agg.total_downed || 0),
      color: 'text-warning',
      bg: 'from-warning/20 to-warning/5',
      barColor: 'bg-warning',
      unit: '次',
      percent: Math.min((agg.total_downed / maxDowned) * 100, 100)
    },
    {
      icon: 'pi pi-chart-line',
      label: '平均DPS',
      value: fmtCompact(agg.avg_dps),
      color: 'text-primary',
      bg: 'from-primary/20 to-primary/5',
      barColor: 'bg-primary',
      unit: '',
      percent: Math.min((agg.avg_dps / maxDps) * 100, 100)
    },
  ]
})
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
    <div
      v-for="kpi in kpiList"
      :key="kpi.label"
      class="card p-4 rounded-xl bg-gradient-to-br border border-transparent hover:border-primary/20 transition-all"
      :class="kpi.bg"
    >
      <div class="flex items-center gap-2 mb-2">
        <i :class="['pi', kpi.icon, 'text-sm', kpi.color]" />
        <span class="text-xs text-neutral-text-secondary">{{ kpi.label }}</span>
      </div>
      <div class="text-xl font-bold text-neutral-text mb-2">
        {{ kpi.value }}
        <span
          v-if="kpi.unit"
          class="text-xs font-normal text-neutral-text-secondary"
        >{{ kpi.unit }}</span>
      </div>
      <div class="h-1 bg-neutral-bg rounded-full overflow-hidden">
        <div
          class="h-full transition-all duration-500"
          :class="kpi.barColor"
          :style="{ width: kpi.percent + '%' }"
        />
      </div>
    </div>
  </div>
</template>
