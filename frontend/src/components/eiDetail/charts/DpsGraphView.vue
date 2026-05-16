<template>
  <div class="dps-graph-view">
    <DpsGraphControls
      v-model="activeMode"
      v-model:time-interval="timeInterval"
    />

    <div class="graph-container card">
      <DpsGraphLegend :title="graphTitle" :players="displayPlayers" />
      <DpsGraphChart
        :lines="chartLines"
        :y-axis-ticks="yAxisTicks"
        :x-axis-ticks="xAxisTicks"
      />
    </div>

    <DpsGraphSummary
      :peak-dps="peakDps"
      :avg-dps="avgDps"
      :min-dps="minDps"
    />
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { computed, ref } from 'vue'
import DpsGraphControls, { type GraphMode } from './DpsGraphControls.vue'
import DpsGraphLegend from './DpsGraphLegend.vue'
import DpsGraphChart from './DpsGraphChart.vue'
import DpsGraphSummary from './DpsGraphSummary.vue'

interface Props {
  players: Player[]
  durationMs: number
  selectedPlayerId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedPlayerId: null
})

const activeMode = ref<GraphMode>('dps')
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

const chartLines = computed(() => {
  return displayPlayers.value.map(player => {
    const data = getPlayerDataPoints(player)
    if (data.length < 2) {
      return { instanceID: player.instanceID, style: {} as Record<string, string> }
    }
    const points = data.map((val, idx) => {
      const x = (idx / Math.max(data.length - 1, 1)) * 100
      const y = 100 - (val / maxValue.value) * 100
      return `${x},${y}`
    }).join(' ')
    return {
      instanceID: player.instanceID,
      style: {
        clipPath: `polygon(${points}, 100% 100%, 0% 100%)`,
        backgroundColor: player.color + '30'
      }
    }
  })
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
</script>

<style scoped lang="css">
.dps-graph-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.graph-container {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}
</style>
