<template>
  <div class="dps-graph-view">
    <div class="graph-controls card">
      <div class="control-group">
        <span class="control-label">图表类型</span>
        <div class="control-buttons">
          <button
            v-for="mode in graphModes"
            :key="mode.key"
            class="control-btn"
            :class="{ active: activeMode === mode.key }"
            @click="activeMode = mode.key"
          >
            {{ mode.label }}
          </button>
        </div>
      </div>
      <div class="control-group">
        <span class="control-label">时间间隔</span>
        <select
          v-model="timeInterval"
          class="control-select"
        >
          <option :value="1">
            1�?
          </option>
          <option :value="5">
            5�?
          </option>
          <option :value="10">
            10�?
          </option>
        </select>
      </div>
    </div>

    <div class="graph-container card">
      <div class="graph-header">
        <h3 class="graph-title">
          <i class="pi pi-chart-line" />
          {{ graphTitle }}
        </h3>
        <div class="graph-legend">
          <div
            v-for="player in displayPlayers"
            :key="player.instanceID"
            class="legend-item"
          >
            <span
              class="legend-color"
              :style="{ backgroundColor: player.color }"
            />
            <span class="legend-name">{{ player.name }}</span>
          </div>
        </div>
      </div>
      <div class="graph-body">
        <div class="y-axis">
          <span
            v-for="(tick, idx) in yAxisTicks"
            :key="idx"
            class="y-tick"
          >{{ formatDamage(tick) }}</span>
        </div>
        <div class="graph-area">
          <div
            v-for="player in displayPlayers"
            :key="player.instanceID"
            class="graph-line"
            :style="getLineStyle(player)"
          />
          <div class="graph-bars">
            <div
              v-for="(_, idx) in xAxisTicks"
              :key="idx"
              class="x-tick-line"
              :style="{ left: (idx / (xAxisTicks.length - 1)) * 100 + '%' }"
            />
          </div>
        </div>
      </div>
      <div class="x-axis">
        <span
          v-for="(tick, idx) in xAxisTicks"
          :key="idx"
          class="x-tick"
        >{{ tick }}s</span>
      </div>
    </div>

    <!-- 统计摘要 -->
    <div class="graph-summary card">
      <div class="summary-grid">
        <div class="summary-item">
          <span class="summary-label">峰值DPS</span>
          <span class="summary-value">{{ formatDamage(peakDps) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">平均DPS</span>
          <span class="summary-value">{{ formatDamage(avgDps) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">最低DPS</span>
          <span class="summary-value">{{ formatDamage(minDps) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">波动幅度</span>
          <span class="summary-value">{{ formatDamage(peakDps - minDps) }}</span>
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

<style scoped lang="css">
.dps-graph-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.graph-controls {
  display: flex;
  gap: 1.5rem;
  padding: 1rem 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.control-buttons {
  display: flex;
  gap: 0.25rem;
}

.control-btn {
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-bg);
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover {
  border-color: var(--color-primary-alpha-30);
}

.control-btn.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.control-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.8125rem;
}

.graph-container {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.graph-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.graph-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.graph-title i {
  color: var(--color-primary);
}

.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-name {
  color: var(--color-text-secondary);
}

.graph-body {
  display: flex;
  height: 300px;
  gap: 0.5rem;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-right: 0.5rem;
  width: 60px;
}

.y-tick {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.graph-area {
  flex: 1;
  position: relative;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  overflow: hidden;
}

.graph-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.6;
}

.graph-bars {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.x-tick-line {
  position: absolute;
  top: 0;
  width: 1px;
  height: 100%;
  background-color: var(--color-border);
  opacity: 0.3;
}

.x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  padding-left: 68px;
}

.x-tick {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.graph-summary {
  padding: 1rem 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}
</style>
