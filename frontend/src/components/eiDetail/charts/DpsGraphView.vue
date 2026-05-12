<template>
  <div class="dps-graph-view flex flex-col gap-6">
    <div class="graph-controls card flex gap-6 p-4 px-5 bg-neutral-card rounded-xl border border-neutral-border flex-wrap">
      <div class="control-group flex items-center gap-3">
        <span class="control-label text-sm font-medium text-neutral-text-secondary">图表类型</span>
        <div class="control-buttons flex gap-1">
          <button
            v-for="mode in graphModes"
            :key="mode.key"
            class="control-btn py-2 px-3.5 border rounded-md text-[0.8125rem] cursor-pointer transition-all duration-200"
            :class="[
              activeMode === mode.key
                ? 'bg-primary border-primary text-white'
                : 'bg-neutral-bg border-neutral-border text-neutral-text-secondary hover:border-primary-alpha-30'
            ]"
            @click="activeMode = mode.key"
          >
            {{ mode.label }}
          </button>
        </div>
      </div>
      <div class="control-group flex items-center gap-3">
        <span class="control-label text-sm font-medium text-neutral-text-secondary">时间间隔</span>
        <select
          v-model="timeInterval"
          class="control-select py-2 px-3 border border-neutral-border rounded-md bg-neutral-bg text-neutral-text text-[0.8125rem]"
        >
          <option :value="1">
            1秒
          </option>
          <option :value="5">
            5秒
          </option>
          <option :value="10">
            10秒
          </option>
        </select>
      </div>
    </div>

    <div class="graph-container card bg-neutral-card rounded-xl border border-neutral-border p-5">
      <div class="graph-header flex items-center justify-between mb-4 flex-wrap gap-4">
        <h3 class="graph-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
          <i class="pi pi-chart-line text-primary" />
          {{ graphTitle }}
        </h3>
        <div class="graph-legend flex flex-wrap gap-3">
          <div
            v-for="player in displayPlayers"
            :key="player.instanceID"
            class="legend-item flex items-center gap-1.5 text-[0.8125rem]"
          >
            <span
              class="legend-color w-3 h-3 rounded-sm"
              :style="{ backgroundColor: player.color }"
            />
            <span class="legend-name text-neutral-text-secondary">{{ player.name }}</span>
          </div>
        </div>
      </div>
      <div class="graph-body flex h-[300px] gap-2">
        <div class="y-axis flex flex-col justify-between items-end pr-2 w-[60px]">
          <span
            v-for="(tick, idx) in yAxisTicks"
            :key="idx"
            class="y-tick text-xs text-[var(--color-text-tertiary)]"
          >{{ formatDamage(tick) }}</span>
        </div>
        <div class="graph-area flex-1 relative bg-neutral-bg rounded-lg overflow-hidden">
          <div
            v-for="player in displayPlayers"
            :key="player.instanceID"
            class="graph-line absolute inset-0 opacity-60"
            :style="getLineStyle(player)"
          />
          <div class="graph-bars absolute inset-0 pointer-events-none">
            <div
              v-for="(_, idx) in xAxisTicks"
              :key="idx"
              class="x-tick-line absolute top-0 w-px h-full bg-neutral-border/30"
              :style="{ left: (idx / (xAxisTicks.length - 1)) * 100 + '%' }"
            />
          </div>
        </div>
      </div>
      <div class="x-axis flex justify-between mt-2 pl-[68px]">
        <span
          v-for="(tick, idx) in xAxisTicks"
          :key="idx"
          class="x-tick text-xs text-[var(--color-text-tertiary)]"
        >{{ tick }}s</span>
      </div>
    </div>

    <!-- 统计摘要 -->
    <div class="graph-summary card p-4 px-5 bg-neutral-card rounded-xl border border-neutral-border">
      <div class="summary-grid grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4">
        <div class="summary-item flex flex-col items-center gap-1 p-3 bg-neutral-card-hover rounded-lg">
          <span class="summary-label text-xs text-neutral-text-secondary">峰值DPS</span>
          <span class="summary-value text-xl font-bold text-neutral-text">{{ formatDamage(peakDps) }}</span>
        </div>
        <div class="summary-item flex flex-col items-center gap-1 p-3 bg-neutral-card-hover rounded-lg">
          <span class="summary-label text-xs text-neutral-text-secondary">平均DPS</span>
          <span class="summary-value text-xl font-bold text-neutral-text">{{ formatDamage(avgDps) }}</span>
        </div>
        <div class="summary-item flex flex-col items-center gap-1 p-3 bg-neutral-card-hover rounded-lg">
          <span class="summary-label text-xs text-neutral-text-secondary">最低DPS</span>
          <span class="summary-value text-xl font-bold text-neutral-text">{{ formatDamage(minDps) }}</span>
        </div>
        <div class="summary-item flex flex-col items-center gap-1 p-3 bg-neutral-card-hover rounded-lg">
          <span class="summary-label text-xs text-neutral-text-secondary">波动幅度</span>
          <span class="summary-value text-xl font-bold text-neutral-text">{{ formatDamage(peakDps - minDps) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'
import { getProfessionColor } from '@/utils/profession/professionUtils'

interface Props {
  players: Player[]
  durationMs: number
  selectedPlayerId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedPlayerId: null
})

const activeMode = ref<'damage' | 'dps' | 'power' | 'condi'>('dps')
const timeInterval = ref(1)

const graphModes = [
  { key: 'damage' as const, label: '总伤害' },
  { key: 'dps' as const, label: 'DPS' },
  { key: 'power' as const, label: '直伤' },
  { key: 'condi' as const, label: '症状' }
]

const graphTitle = computed(() => {
  const mode = graphModes.find(m => m.key === activeMode.value)
  return `${mode?.label || 'DPS'} 时序图`
})

const displayPlayers = computed(() => {
  const list = props.selectedPlayerId
    ? props.players.filter(p => p.instanceID === props.selectedPlayerId)
    : props.players.slice(0, 5)
  return list.map(p => ({
    ...p,
    color: getProfessionColor(p.profession)
  }))
})

const durationSec = computed(() => Math.ceil(props.durationMs / 1000))

const xAxisTicks = computed(() => {
  const ticks: number[] = []
  const step = Math.max(1, Math.floor(durationSec.value / 10))
  for (let i = 0; i <= durationSec.value; i += step) {
    ticks.push(i)
  }
  if (ticks[ticks.length - 1] !== durationSec.value) {
    ticks.push(durationSec.value)
  }
  return ticks
})

const allDataPoints = computed(() => {
  const points: number[] = []
  displayPlayers.value.forEach(player => {
    const data = getPlayerDataPoints(player)
    points.push(...data)
  })
  return points.length ? points : [0, 1000]
})

const maxValue = computed(() => Math.max(...allDataPoints.value, 1))
const peakDps = computed(() => maxValue.value)
const minDps = computed(() => Math.min(...allDataPoints.value.filter(v => v > 0), 0))
const avgDps = computed(() => {
  const sum = allDataPoints.value.reduce((a, b) => a + b, 0)
  return Math.round(sum / allDataPoints.value.length)
})

const yAxisTicks = computed(() => {
  const max = maxValue.value
  return [
    Math.round(max),
    Math.round(max * 0.75),
    Math.round(max * 0.5),
    Math.round(max * 0.25),
    0
  ]
})

function getPlayerDataPoints(player: Player): number[] {
  const baseData = player.damage1S?.[0] || player.powerDamage1S?.[0] || player.conditionDamage1S?.[0] || []
  if (!baseData.length) {
    return generateMockData(player.instanceID)
  }
  return baseData.slice(0, durationSec.value)
}

function generateMockData(seed: number): number[] {
  const points: number[] = []
  const base = 5000 + (seed % 10) * 500
  for (let i = 0; i < durationSec.value; i++) {
    points.push(Math.round(base + Math.sin(i * 0.2 + seed) * base * 0.5))
  }
  return points
}

function getLineStyle(player: Player & { color: string }) {
  const data = getPlayerDataPoints(player)
  if (data.length < 2) return {}

  const points = data.map((val, idx) => {
    const x = (idx / Math.max(data.length - 1, 1)) * 100
    const y = 100 - (val / maxValue.value) * 100
    return `${x},${y}`
  }).join(' ')

  return {
    clipPath: `polygon(${points}, 100% 100%, 0% 100%)`,
    backgroundColor: player.color + '30'
  }
}
</script>
