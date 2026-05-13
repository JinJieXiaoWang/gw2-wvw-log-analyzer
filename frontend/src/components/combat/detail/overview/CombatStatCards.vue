<template>
  <div class="card p-5 rounded-xl border-neutral-border/50">
    <h3 class="text-sm font-semibold text-neutral-text mb-5 flex items-center gap-2">
      <div class="p-1.5 rounded-lg bg-primary/10">
        <i class="pi pi-chart-bar text-primary" />
      </div>
      战斗属性统计
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
            :size="48"
            :stroke-width="8"
            :radius="42"
            track-color="var(--color-border)"
            :segments="[
              { color: '#165DFF', value: agg.total_power_damage },
              { color: '#22c55e', value: agg.total_condi_damage + agg.total_breakbar_damage },
            ]"
          >
            <i class="pi pi-chart-pie text-primary text-sm" />
          </DonutChart>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(donut.total) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            伤害构成
          </p>
        </div>
      </div>

      <!-- 保护覆盖率 -->
      <div
        class="card p-3 rounded-xl border-info/20 bg-gradient-to-br from-info/5 to-transparent hover:border-info/40 hover:shadow-lg hover:shadow-info/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'protection', '保护覆盖率')"
      >
        <div class="flex flex-col items-center">
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
                stroke="#3b82f6"
                stroke-width="8"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * averages.protection / 100)"
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
            保护
          </p>
        </div>
      </div>

      <!-- 稳固覆盖率 -->
      <div
        class="card p-3 rounded-xl border-warning/20 bg-gradient-to-br from-warning/5 to-transparent hover:border-warning/40 hover:shadow-lg hover:shadow-warning/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'stability', '稳固覆盖率')"
      >
        <div class="flex flex-col items-center">
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
                stroke="#f59e0b"
                stroke-width="8"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * averages.stability / 100)"
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
            稳固
          </p>
        </div>
      </div>

      <!-- 清症总数 -->
      <div
        class="card p-3 rounded-xl border-success/20 bg-gradient-to-br from-success/5 to-transparent hover:border-success/40 hover:shadow-lg hover:shadow-success/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'condition_cleanses', '清症统计')"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-success/10 mb-2">
            <i class="pi pi-heart text-success text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(agg.total_condition_cleanses) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            清症
          </p>
        </div>
      </div>

      <!-- 削增益总数 -->
      <div
        class="card p-3 rounded-xl border-error/20 bg-gradient-to-br from-error/5 to-transparent hover:border-error/40 hover:shadow-lg hover:shadow-error/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'boon_strips', '削增益统计')"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-error/10 mb-2">
            <i class="pi pi-minus-circle text-error text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(agg.total_boon_strips) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            削增益
          </p>
        </div>
      </div>

      <!-- 承伤总量 -->
      <div
        class="card p-3 rounded-xl border-secondary/20 bg-gradient-to-br from-secondary/5 to-transparent hover:border-secondary/40 hover:shadow-lg hover:shadow-secondary/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'damage_taken', '承伤统计')"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-secondary/10 mb-2">
            <i class="pi pi-exclamation-triangle text-secondary text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ fmtCompact(agg.total_damage_taken) }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            承伤
          </p>
        </div>
      </div>

      <!-- 命中率 -->
      <div
        class="card p-3 rounded-xl border-primary/20 bg-gradient-to-br from-primary/5 to-transparent hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'hitRate', '命中率统计')"
      >
        <div class="flex flex-col items-center">
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
                stroke="#165DFF"
                stroke-width="8"
                :stroke-dasharray="264"
                :stroke-dashoffset="264 - (264 * averages.hitRate / 100)"
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
            命中率
          </p>
        </div>
      </div>

      <!-- 击倒控制 -->
      <div
        class="card p-3 rounded-xl border-warning/20 bg-gradient-to-br from-warning/5 to-transparent hover:border-warning/40 hover:shadow-lg hover:shadow-warning/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'control', '击倒控制统计')"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-warning/10 mb-2">
            <i class="pi pi-arrow-down text-warning text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ agg.total_downed || 0 }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            击倒
          </p>
        </div>
      </div>

      <!-- 技能效率 -->
      <div
        class="card p-3 rounded-xl border-secondary/20 bg-gradient-to-br from-secondary/5 to-transparent hover:border-secondary/40 hover:shadow-lg hover:shadow-secondary/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'efficiency', '技能效率统计')"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-secondary/10 mb-2">
            <i class="pi pi-cog text-secondary text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.skillCastUptime?.toFixed(0) ?? 0 }}%
          </p>
          <p class="text-xs text-neutral-text-secondary">
            施法占比
          </p>
        </div>
      </div>

      <!-- 位置协同 -->
      <div
        class="card p-3 rounded-xl border-info/20 bg-gradient-to-br from-info/5 to-transparent hover:border-info/40 hover:shadow-lg hover:shadow-info/10 transition-all duration-300 cursor-pointer"
        @click="emit('open-stat-detail', 'position', '位置协同统计')"
      >
        <div class="flex flex-col items-center">
          <div class="p-2 rounded-lg bg-info/10 mb-2">
            <i class="pi pi-map-marker text-info text-lg" />
          </div>
          <p class="text-lg font-bold text-neutral-text">
            {{ averages.stackDist?.toFixed(0) ?? 0 }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            堆叠距离
          </p>
          <p class="text-[10px] text-neutral-text-secondary mt-1">
            指挥距离 {{ averages.distToCom?.toFixed(0) ?? 0 }}
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
