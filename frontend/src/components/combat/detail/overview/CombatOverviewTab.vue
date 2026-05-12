<script setup lang="ts">
import { computed } from 'vue'
import type { EiAnalysisResponse, EiAnalysisAggregate, EiAnalysisFight } from '@/services/ei/eiAnalysisService'
import CombatKpiCards from '@/components/combat/detail/overview/CombatKpiCards.vue'
import CombatStatCards from '@/components/combat/detail/overview/CombatStatCards.vue'
import CombatDetailStats from '@/components/combat/detail/overview/CombatDetailStats.vue'
import { fmtCompact, getProfessionColor, getProfessionName, groupColor } from '@/composables/combat/useCombatHelpers'

const props = defineProps<{
  summary: EiAnalysisResponse | null
  agg: EiAnalysisAggregate
  fightSummary: EiAnalysisFight
  statAverages: Record<string, number>
  donut: any
  groups: any[]
}>()

const emit = defineEmits<{
  'open-stat-detail': [type: string, title: string]
  'show-damage-detail': []
}>()

const powerPct = computed(() => props.summary?.percentages?.power || 0)
const condiPct = computed(() => props.summary?.percentages?.condi || 0)
const breakbarPct = computed(() => props.summary?.percentages?.breakbar || 0)
</script>

<template>
  <div class="space-y-5">
    <CombatKpiCards :agg="agg" />

    <CombatStatCards
      :agg="agg"
      :averages="statAverages"
      :donut="donut"
      @show-damage-detail="emit('show-damage-detail')"
      @open-stat-detail="(type, title) => emit('open-stat-detail', type, title)"
    />

    <!-- 职业分布 -->
    <div class="card p-4 rounded-xl border-neutral-border/50">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
          <div class="p-1.5 rounded-lg bg-info/10">
            <i class="pi pi-users text-info" />
          </div>
          职业分布
        </h3>
        <span class="text-xs text-neutral-text-secondary">{{ summary?.total_players || 0 }} 人参战</span>
      </div>
      <div class="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-2">
        <div
          v-for="(count, prof) in summary?.profession_distribution"
          :key="prof"
            class="flex flex-col items-center p-2 rounded-lg bg-neutral-bg/50
                   hover:bg-neutral-bg-secondary transition-all"
        >
          <span
            class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-1"
            :style="{ backgroundColor: getProfessionColor(prof) + '20', color: getProfessionColor(prof) }"
          >{{ count }}</span>
          <span
            class="text-[10px] text-center"
            :style="{ color: getProfessionColor(prof) }"
          >{{ getProfessionName(prof) }}</span>
        </div>
      </div>
    </div>

    <CombatDetailStats
      :players="summary?.players || []"
      :agg="agg"
      :power-pct="powerPct"
      :condi-pct="condiPct"
      :breakbar-pct="breakbarPct"
    />

    <!-- 小队对比分析 -->
    <div
      v-if="groups.length > 0"
      class="card p-5 rounded-xl border-neutral-border/50"
    >
      <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-primary/10">
          <i class="pi pi-chart-bar text-primary" />
        </div>
        小队对比分析
      </h3>
      <div class="space-y-3">
        <div
          v-for="g in groups"
          :key="g.id"
          class="flex items-center gap-4"
        >
          <span
            class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                   text-white flex-shrink-0"
            :style="{ backgroundColor: groupColor(g.id) }"
          >{{ g.id }}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-neutral-text-secondary">小队 {{ g.id }} · {{ g.players.length }}人</span>
              <span class="text-xs font-semibold text-primary">{{ fmtCompact(g.total_damage) }}</span>
            </div>
            <div class="h-2 bg-neutral-bg rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700"
                :style="{ width: g.bar_width + '%', backgroundColor: groupColor(g.id) }"
              />
            </div>
          </div>
          <div class="flex items-center gap-3 text-xs flex-shrink-0">
            <div class="text-center">
              <span class="block font-semibold text-neutral-text">{{ fmtCompact(g.avg_dps) }}</span>
              <span class="text-neutral-text-secondary">平均DPS</span>
            </div>
            <div class="text-center">
              <span class="block font-semibold text-error">{{ g.total_dead }}</span>
              <span class="text-neutral-text-secondary">死亡</span>
            </div>
            <div class="text-center">
              <span class="block font-semibold text-warning">{{ g.total_downed }}</span>
              <span class="text-neutral-text-secondary">击倒</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
