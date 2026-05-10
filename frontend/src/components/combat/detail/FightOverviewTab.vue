<template>
  <div class="space-y-5">
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
      <div v-for="(k, idx) in data.kpiList" :key="k.label" class="card p-4 rounded-xl border border-neutral-border/50 hover:border-primary/30 transition-all hover:shadow-lg group" :class="k.bg" :style="{ animationDelay: `${idx * 100}ms` }">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-medium text-neutral-text-secondary/80 uppercase">{{ k.label }}</span>
          <div class="p-2 rounded-lg bg-white/5 group-hover:bg-white/10 transition-colors"><i :class="k.icon + ' ' + k.color + ' text-lg'" /></div>
        </div>
        <div class="flex items-end">
          <p class="text-2xl font-bold text-neutral-text">{{ k.value }}</p>
          <span class="ml-2 text-xs text-neutral-text-secondary mb-1">{{ k.unit }}</span>
        </div>
        <div class="mt-2 h-1 bg-white/10 rounded-full overflow-hidden"><div class="h-full rounded-full transition-all duration-700" :class="k.barColor" :style="{ width: k.percent + '%' }" /></div>
      </div>
    </div>
    <div class="card p-5 rounded-xl border-neutral-border/50">
      <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2"><div class="p-1.5 rounded-lg bg-primary/10"><i class="pi pi-chart-bar text-primary" /></div>战斗属性统计</h3>
      <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 xl:grid-cols-10 gap-3">
        <div v-for="s in statCards" :key="s.key" class="card p-3 rounded-xl border hover:shadow-lg transition-all cursor-pointer flex flex-col items-center" :class="[s.border, s.bg]" @click="emit('open-stat-detail', s.category, s.dialogTitle)">
          <template v-if="s.type === 'multi-ring'">
            <div class="relative w-12 h-12 mb-2">
              <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-border)" stroke-width="8" />
                <circle cx="50" cy="50" r="42" fill="none" stroke="#165DFF" stroke-width="8" :stroke-dasharray="data.donut.pd" />
                <circle cx="50" cy="50" r="42" fill="none" stroke="#22c55e" stroke-width="8" :stroke-dasharray="data.donut.cd" :stroke-dashoffset="data.donut.co" />
              </svg>
              <div class="absolute inset-0 flex items-center justify-center"><i :class="s.icon + ' text-primary text-sm'" /></div>
            </div>
          </template>
          <template v-else-if="s.type === 'ring'">
            <div class="relative w-12 h-12 mb-2">
              <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-border)" stroke-width="8" />
                <circle cx="50" cy="50" r="42" fill="none" :stroke="s.ringColor" stroke-width="8" :stroke-dasharray="264" :stroke-dashoffset="264 - (264 * s.percent / 100)" stroke-linecap="round" />
              </svg>
              <div class="absolute inset-0 flex items-center justify-center"><i :class="s.icon + ' text-' + s.color + ' text-sm'" /></div>
            </div>
          </template>
          <template v-else>
            <div class="p-2 rounded-lg mb-2" :class="'bg-' + s.color + '/10'"><i :class="s.icon + ' text-' + s.color + ' text-lg'" /></div>
          </template>
          <p class="text-lg font-bold text-neutral-text">{{ s.value }}</p>
          <p class="text-xs text-neutral-text-secondary">{{ s.label }}</p>
        </div>
      </div>
    </div>
    <div class="card p-4 rounded-xl border-neutral-border/50">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2"><div class="p-1.5 rounded-lg bg-info/10"><i class="pi pi-users text-info" /></div>ְҵ分布</h3>
        <span class="text-xs text-neutral-text-secondary">{{ data.summary?.total_players || 0 }} 人参鎴?/span>
      </div>
      <div class="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-2">
        <div v-for="(count, prof) in data.summary?.profession_distribution || {}" :key="prof" class="flex flex-col items-center p-2 rounded-lg bg-neutral-bg/50 hover:bg-neutral-bg-secondary transition-all">
          <span class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-1" :style="profStyle(prof)">{{ count }}</span>
          <span class="text-[10px] text-center px-1 rounded" :style="profStyle(prof)">{{ getProfessionName(prof) }}</span>
        </div>
      </div>
    </div>
    <div class="card p-5 rounded-xl border-neutral-border/50">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2"><div class="p-1.5 rounded-lg bg-secondary/10"><i class="pi pi-sliders-h text-secondary" /></div>璇︾粏战斗统计</h3>
        <BaseButton :label="showDetail ? '收起' : 'չ开'" :icon="showDetail ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" severity="secondary" size="small" @click="showDetail = !showDetail" />
      </div>
      <div v-show="showDetail" class="space-y-4">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div v-for="card in damageCards" :key="card.label" class="card p-4 rounded-xl text-center" :class="[card.border, card.bg]">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-medium text-neutral-text-secondary uppercase">{{ card.label }}</span>
              <div class="p-1.5 rounded-lg" :class="card.iconBg"><i :class="card.icon + ' text-sm ' + card.iconColor" /></div>
            </div>
            <p class="text-3xl font-bold" :class="card.valueColor">{{ card.value }}</p>
            <div class="mt-2 flex items-center justify-center gap-2">
              <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden"><div class="h-full rounded-full transition-all duration-700" :class="card.barColor" :style="{ width: card.percent + '%' }" /></div>
              <span class="text-sm font-semibold" :class="card.valueColor">{{ card.percent }}%</span>
            </div>
          </div>
        </div>
        <FightPlayerStatsTable :players="data.summary?.players || []" />
      </div>
    </div>
    <div v-if="data.groups.length > 0" class="card p-5 rounded-xl border-neutral-border/50">
      <h3 class="text-sm font-semibold text-neutral-text mb-3 flex items-center gap-2"><div class="p-1.5 rounded-lg bg-primary/10"><i class="pi pi-chart-bar text-primary" /></div>小队对比分析</h3>
      <div class="space-y-3">
        <div v-for="g in data.groups" :key="g.id" class="flex items-center gap-4">
          <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0" :style="{ backgroundColor: groupColor(g.id) }">{{ g.id }}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-neutral-text-secondary">小队 {{ g.id }} · {{ g.players.length }}人</span>
              <span class="text-xs font-semibold text-primary">{{ fmtCompact(getTeamTotalDamage(g)) }}</span>
            </div>
            <div class="h-2 bg-neutral-bg rounded-full overflow-hidden"><div class="h-full rounded-full transition-all duration-700" :style="teamBarStyle(g)" /></div>
          </div>
          <div class="flex items-center gap-3 text-xs flex-shrink-0">
            <div class="text-center"><span class="block font-semibold text-neutral-text">{{ fmtCompact(getTeamAvgDps(g)) }}</span><span class="text-neutral-text-secondary">平均DPS</span></div>
            <div class="text-center"><span class="block font-semibold text-error">{{ getTeamDeathCount(g) }}</span><span class="text-neutral-text-secondary">死亡</span></div>
            <div class="text-center"><span class="block font-semibold text-warning">{{ getTeamDownedCount(g) }}</span><span class="text-neutral-text-secondary">击倒</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import BaseButton from '@/components/common/ui/BaseButton.vue'
import FightPlayerStatsTable from './FightPlayerStatsTable.vue'
import { getProfessionColor, getProfessionName } from '@/utils/profession/professionUtils'
import { groupColor } from '@/utils/combat/combatFormatters'
import { type StatCategory, getTeamTotalDamage, getTeamAvgDps, getTeamDeathCount, getTeamDownedCount } from '@/utils/combat/combatStats'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import type { KpiItem, DonutData, StatAverages, GroupData } from '@/composables/combat/useCombatLogDetail'
import type { EiAnalysisResponse, EiAnalysisFight, EiAnalysisAggregate, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

interface OverviewData {
  summary: EiAnalysisResponse | null
  fightSummary: EiAnalysisFight
  agg: EiAnalysisAggregate
  kpiList: KpiItem[]
  donut: DonutData
  statAverages: StatAverages
  groups: GroupData[]
  powerPct: number
  condiPct: number
  breakbarPct: number
}

const props = defineProps<{ data: OverviewData }>()
const emit = defineEmits<{
  'open-stat-detail': [type: StatCategory, title: string]
  'open-player-dialog': [player: EiAnalysisPlayer]
}>()

const showDetail = ref(false)

const statCards = computed(() => {
  const d = props.data
  const sa = d.statAverages
  return [
    { type: 'multi-ring' as const, key: 'damage', label: '输出伤害', category: 'damage_output' as StatCategory, dialogTitle: '输出伤害统计', value: fmtCompact(d.donut.total), icon: 'pi pi-chart-pie', color: 'primary', border: 'border-primary/20', bg: 'bg-gradient-to-br from-primary/5 to-transparent' },
    { type: 'ring' as const, key: 'protection', label: '保护', category: 'protection' as StatCategory, dialogTitle: '保护覆盖率', value: sa.protection.toFixed(0) + '%', icon: 'pi pi-shield', color: 'info', ringColor: '#3b82f6', percent: sa.protection, border: 'border-info/20', bg: 'bg-gradient-to-br from-info/5 to-transparent' },
    { type: 'ring' as const, key: 'stability', label: '稳固', category: 'stability' as StatCategory, dialogTitle: '稳固覆盖率', value: sa.stability.toFixed(0) + '%', icon: 'pi pi-lock', color: 'warning', ringColor: '#f59e0b', percent: sa.stability, border: 'border-warning/20', bg: 'bg-gradient-to-br from-warning/5 to-transparent' },
    { type: 'icon' as const, key: 'cleanses', label: '清症', category: 'condition_cleanses' as StatCategory, dialogTitle: '清症统计', value: fmtCompact(d.agg.total_condition_cleanses), icon: 'pi pi-heart', color: 'success', border: 'border-success/20', bg: 'bg-gradient-to-br from-success/5 to-transparent' },
    { type: 'icon' as const, key: 'strips', label: '削增益', category: 'boon_strips' as StatCategory, dialogTitle: '削增益统计', value: fmtCompact(d.agg.total_boon_strips), icon: 'pi pi-minus-circle', color: 'error', border: 'border-error/20', bg: 'bg-gradient-to-br from-error/5 to-transparent' },
    { type: 'icon' as const, key: 'taken', label: '承伤', category: 'damage_taken' as StatCategory, dialogTitle: '承伤统计', value: fmtCompact(d.agg.total_damage_taken), icon: 'pi pi-exclamation-triangle', color: 'secondary', border: 'border-secondary/20', bg: 'bg-gradient-to-br from-secondary/5 to-transparent' },
    { type: 'ring' as const, key: 'hitRate', label: '命中率', category: 'hitRate' as StatCategory, dialogTitle: '命中率统计', value: sa.hitRate.toFixed(1) + '%', icon: 'pi pi-bolt', color: 'primary', ringColor: '#165DFF', percent: sa.hitRate, border: 'border-primary/20', bg: 'bg-gradient-to-br from-primary/5 to-transparent' },
    { type: 'icon' as const, key: 'control', label: '击倒', category: 'control' as StatCategory, dialogTitle: '击倒与控制能力统计', value: String(d.agg.total_downed || 0), icon: 'pi pi-arrow-down', color: 'warning', border: 'border-warning/20', bg: 'bg-gradient-to-br from-warning/5 to-transparent' },
    { type: 'icon' as const, key: 'efficiency', label: '施法占比', category: 'efficiency' as StatCategory, dialogTitle: '技能效率统计', value: (sa.skillCastUptime?.toFixed(0) ?? '0') + '%', icon: 'pi pi-cog', color: 'secondary', border: 'border-secondary/20', bg: 'bg-gradient-to-br from-secondary/5 to-transparent' },
    { type: 'icon' as const, key: 'position', label: '堆叠距离', category: 'position' as StatCategory, dialogTitle: '位置协同统计', value: sa.stackDist?.toFixed(0) ?? '0', icon: 'pi pi-map-marker', color: 'info', border: 'border-info/20', bg: 'bg-gradient-to-br from-info/5 to-transparent' },
  ]
})

const damageCards = computed(() => {
  const d = props.data
  return [
    { label: '直伤总量', value: fmtCompact(d.agg.total_power_damage), percent: d.powerPct, icon: 'pi pi-bolt', iconColor: 'text-primary', iconBg: 'bg-primary/20', border: 'border-primary/20', bg: 'bg-gradient-to-br from-primary/10 to-transparent', valueColor: 'text-primary', barColor: 'bg-primary' },
    { label: '症状总量', value: fmtCompact(d.agg.total_condi_damage), percent: d.condiPct, icon: 'pi pi-flame', iconColor: 'text-success', iconBg: 'bg-success/20', border: 'border-success/20', bg: 'bg-gradient-to-br from-success/10 to-transparent', valueColor: 'text-success', barColor: 'bg-success' },
    { label: '破甲总量', value: fmtCompact(d.agg.total_breakbar_damage), percent: d.breakbarPct, icon: 'pi pi-hammer', iconColor: 'text-secondary', iconBg: 'bg-secondary/20', border: 'border-secondary/20', bg: 'bg-gradient-to-br from-secondary/10 to-transparent', valueColor: 'text-secondary', barColor: 'bg-secondary' },
  ]
})

function profStyle(prof: string) {
  const c = getProfessionColor(prof)
  return { backgroundColor: c + '20', color: c }
}

function teamBarStyle(g: GroupData) {
  const totalDmg = props.data.groups.reduce((s, x) => s + getTeamTotalDamage(x), 0)
  const avgDmg = totalDmg / Math.max(props.data.groups.length, 1)
  const teamDmg = getTeamTotalDamage(g)
  const width = Math.min((teamDmg / Math.max(avgDmg, 1)) * 50, 100)
  return { width: width + '%', backgroundColor: groupColor(g.id) }
}
</script>
