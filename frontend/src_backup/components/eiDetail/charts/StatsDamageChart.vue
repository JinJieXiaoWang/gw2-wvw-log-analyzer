<template>
  <div class="damage-chart-section card mb-6">
    <div class="chart-header">
      <h3 class="chart-title">
        <i class="pi pi-chart-line" /> 伤害统计
      </h3>
      <div class="chart-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="chart-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="chart-container">
      <div class="chart-placeholder">
        <div class="chart-content">
          <div class="damage-bars">
            <div
              v-for="(player, index) in topPlayers"
              :key="player.instanceID"
              class="damage-bar-item"
            >
              <div class="bar-label">
                <span
                  class="rank"
                  :class="getRankClass(index)"
                >{{ index + 1 }}</span>
                <span class="name">{{ player.name }}</span>
              </div>
              <div class="bar-container">
                <div
                  class="bar-fill"
                  :style="{ width: getChartValue(player) + '%', backgroundColor: getProfessionColor(player.profession) }"
                />
              </div>
              <div class="bar-value">
                {{ formatLargeNumber(getChartRawValue(player)) }}
              </div>
            </div>
          </div>
        </div>
        <div class="chart-summary">
          <div class="summary-item">
            <span class="label">总伤害</span><span class="value">{{ formatLargeNumber(totalDamage) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">平均DPS</span><span class="value">{{ formatLargeNumber(avgDps) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">战斗时长</span><span class="value">{{ fightDuration }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { getProfessionColor, getProfessionName } from '@/utils/profession/professionUtils'

const { players, totalDamage, avgDps, fightDuration } = defineProps<{
  players: Player[]
  totalDamage: number
  avgDps: number
  fightDuration: string
}>()

const activeTab = defineModel<string>('activeTab', { default: 'damage' })

const tabs = [
  { key: 'damage', label: '伤害' },
  { key: 'dps', label: 'DPS' },
  { key: 'power', label: '直伤' },
  { key: 'condi', label: '症状' },
]

const topPlayers = computed(() => players.slice(0, 5))

function getRankClass(index: number) {
  return index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : ''
}

function getChartValue(player: Player) {
  if (!players.length) return 0
  const max = Math.max(...players.map(p => getChartRawValue(p)))
  return max > 0 ? (getChartRawValue(player) / max) * 100 : 0
}

function getChartRawValue(player: Player) {
  switch (activeTab.value) {
    case 'dps': return player.dps || 0
    case 'power': return player.dpsAll?.[0]?.powerDamage || 0
    case 'condi': return player.dpsAll?.[0]?.condiDamage || 0
    default: return player.dpsAll?.[0]?.damage || 0
  }
}

function formatLargeNumber(num: number): string {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M'
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped>@import '../stats/StatsView.css';</style>
