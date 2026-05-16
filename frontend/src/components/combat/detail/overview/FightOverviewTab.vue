<template>
  <div class="space-y-5">
    <FightOverviewKpiCards :kpi-list="data.kpiList" />
    <FightOverviewStatCards
      :donut="data.donut"
      :stat-averages="data.statAverages"
      :agg="data.agg"
      @open-stat-detail="(...args) => emit('open-stat-detail', ...args)"
    />
    <FightOverviewProfessionDistribution
      :distribution="data.summary?.profession_distribution || {}"
      :total-players="data.summary?.total_players || 0"
    />
    <FightOverviewCombatAnalysis
      :agg="data.agg"
      :power-pct="data.powerPct"
      :condi-pct="data.condiPct"
      :breakbar-pct="data.breakbarPct"
      :players="data.summary?.players || []"
    />
    <FightOverviewSquadComparison
      v-if="data.groups.length > 0"
      :groups="data.groups"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 战斗概览标签页组件
 * 功能：展示战斗统计概览、伤害分析、小队数据
 * 更新：2026-05-12 - 使用后端预计算数据，移除前端计算逻辑
 * 更新：2026-05-16 - 拆分为子组件
 */
import type { EiAnalysisAggregate, EiAnalysisGroup, EiAnalysisPlayer, EiAnalysisFight, EiAnalysisResponse } from '@/services/ei/eiAnalysisService'
import type { DonutData, KpiItem, StatAverages } from '@/composables/combat/useCombatLogDetail'
import { type StatCategory } from '@/utils/combat/combatStats'
import FightOverviewKpiCards from './FightOverviewKpiCards.vue'
import FightOverviewStatCards from './FightOverviewStatCards.vue'
import FightOverviewProfessionDistribution from './FightOverviewProfessionDistribution.vue'
import FightOverviewCombatAnalysis from './FightOverviewCombatAnalysis.vue'
import FightOverviewSquadComparison from './FightOverviewSquadComparison.vue'

interface OverviewData {
  summary: EiAnalysisResponse | null
  fightSummary: EiAnalysisFight
  agg: EiAnalysisAggregate
  kpiList: KpiItem[]
  donut: DonutData
  statAverages: StatAverages
  groups: EiAnalysisGroup[]
  powerPct: number
  condiPct: number
  breakbarPct: number
}

defineProps<{ data: OverviewData }>()

const emit = defineEmits<{
  'open-stat-detail': [type: StatCategory, title: string]
  'open-player-dialog': [player: EiAnalysisPlayer]
}>()
</script>
