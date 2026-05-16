<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold text-neutral-text flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-secondary/10">
          <i class="pi pi-sliders-h text-secondary" />
        </div>{{ SECTION_TITLES.COMBAT_ANALYSIS }}
      </h3>
      <BaseButton
        :label="showDetail ? UI_LABELS.COLLAPSE : UI_LABELS.EXPAND"
        :icon="showDetail ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
        severity="secondary"
        size="small"
        @click="showDetail = !showDetail"
      />
    </div>
    <div
      v-show="showDetail"
      class="space-y-4"
    >
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div
          v-for="card in damageCards"
          :key="card.label"
          class="card p-4 rounded-xl text-center"
          :class="[card.border, card.bg]"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-medium text-neutral-text-secondary uppercase">{{ card.label }}</span>
            <div
              class="p-1.5 rounded-lg"
              :class="card.iconBg"
            >
              <i :class="card.icon + ' text-sm ' + card.iconColor" />
            </div>
          </div>
          <p
            class="text-3xl font-bold"
            :class="card.valueColor"
          >
            {{ card.value }}
          </p>
          <div class="mt-2 flex items-center justify-center gap-2">
            <div class="w-20 h-2 bg-neutral-bg rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700"
                :class="card.barColor"
                :style="{ width: card.percent + '%' }"
              />
            </div>
            <span
              class="text-sm font-semibold"
              :class="card.valueColor"
            >{{ card.percent }}%</span>
          </div>
        </div>
      </div>
      <FightPlayerStatsTable :players="players" />
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import FightPlayerStatsTable from '@/components/combat/detail/tables/FightPlayerStatsTable.vue'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { computed, ref } from 'vue'

const SECTION_TITLES = {
  COMBAT_ANALYSIS: '战斗统计',
} as const

const UI_LABELS = {
  COLLAPSE: '收起',
  EXPAND: '展开',
} as const

const DAMAGE_LABELS = {
  POWER_DAMAGE: '直伤总量',
  CONDI_DAMAGE: '症状总量',
  BREAKBAR_DAMAGE: '破甲总量',
} as const

const props = defineProps<{
  agg: {
    total_power_damage: number
    total_condi_damage: number
    total_breakbar_damage: number
  }
  powerPct: number
  condiPct: number
  breakbarPct: number
  players: EiAnalysisPlayer[]
}>()

const showDetail = ref(false)

const damageCards = computed(() => {
  return [
    { label: DAMAGE_LABELS.POWER_DAMAGE, value: fmtCompact(props.agg.total_power_damage), percent: props.powerPct, icon: 'pi pi-bolt', iconColor: 'text-primary', iconBg: 'bg-primary/20', border: 'border-primary/20', bg: 'bg-gradient-to-br from-primary/10 to-transparent', valueColor: 'text-primary', barColor: 'bg-primary' },
    { label: DAMAGE_LABELS.CONDI_DAMAGE, value: fmtCompact(props.agg.total_condi_damage), percent: props.condiPct, icon: 'pi pi-flame', iconColor: 'text-success', iconBg: 'bg-success/20', border: 'border-success/20', bg: 'bg-gradient-to-br from-success/10 to-transparent', valueColor: 'text-success', barColor: 'bg-success' },
    { label: DAMAGE_LABELS.BREAKBAR_DAMAGE, value: fmtCompact(props.agg.total_breakbar_damage), percent: props.breakbarPct, icon: 'pi pi-hammer', iconColor: 'text-secondary', iconBg: 'bg-secondary/20', border: 'border-secondary/20', bg: 'bg-gradient-to-br from-secondary/10 to-transparent', valueColor: 'text-secondary', barColor: 'bg-secondary' },
  ]
})
</script>
