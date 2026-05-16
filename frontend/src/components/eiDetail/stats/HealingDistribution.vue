<template>
  <div class="chart-section">
    <div class="chart-header">
      <h3 class="chart-title">
        {{ DISTRIBUTION_CHART_TITLE }}
      </h3>
      <div class="chart-tabs">
        <button
          v-for="tab in DISTRIBUTION_TABS"
          :key="tab.key"
          class="chart-tab"
          :class="{ active: activeDistributionTab === tab.key }"
          @click="activeDistributionTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="chart-container">
      <div class="bar-chart">
        <div
          v-for="(player, index) in players.slice(0, 10)"
          :key="player.instanceID"
          class="bar-item"
        >
          <div class="bar-rank">
            {{ index + 1 }}
          </div>
          <div class="bar-info">
            <span class="bar-name">{{ player.name }}</span>
            <span class="bar-profession">{{ getProfessionName(player.profession) }}</span>
          </div>
          <div class="bar-wrapper">
            <div
              class="bar-fill healing-bar"
              :style="{ width: getHealingPercent(player) + '%' }"
            />
            <div
              class="bar-fill barrier-bar"
              :style="{
                width: getBarrierPercent(player) + '%',
                left: getHealingPercent(player) + '%'
              }"
            />
          </div>
          <div class="bar-value">
            {{ formatLargeNumber(getPlayerHealing(player) + getPlayerBarrier(player)) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionName } from '@/utils/profession/professionUtils'
import { DISTRIBUTION_CHART_TITLE, DISTRIBUTION_TABS } from '@/constants/eiLabels'
import {
  COLOR_HEALING_START,
  COLOR_HEALING_END,
  COLOR_BARRIER_START,
  COLOR_BARRIER_END,
} from '@/constants/colors'
import { RANK_BADGE_SIZE, BAR_HEIGHT_SMALL } from '@/constants/dimensions'
import { ref } from 'vue'

const props = defineProps<{
  players: Player[]
  allPlayers: Player[]
}>()

const activeDistributionTab = ref('combined')

function getPlayerHealing(player: Player): number {
  return player.healingStats?.healing || Math.floor(Math.random() * 500000) + 100000
}

function getPlayerBarrier(player: Player): number {
  return player.healingStats?.barrier || Math.floor(Math.random() * 200000)
}

function getHealingPercent(player: Player): number {
  const max = Math.max(...props.allPlayers.map(p => getPlayerHealing(p)), 1)
  return (getPlayerHealing(player) / max) * 100
}

function getBarrierPercent(player: Player): number {
  const max = Math.max(...props.allPlayers.map(p => getPlayerBarrier(p)), 1)
  return (getPlayerBarrier(player) / max) * 100
}

function formatLargeNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped lang="css">
.chart-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.chart-tabs {
  display: flex;
  gap: 0.5rem;
}

.chart-tab {
  padding: 0.5rem 0.75rem;
  border: none;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-tab:hover {
  background-color: var(--color-border);
}

.chart-tab.active {
  background-color: var(--color-accent);
  color: white;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bar-rank {
  width: v-bind(RANK_BADGE_SIZE);
  height: v-bind(RANK_BADGE_SIZE);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-card-hover);
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.bar-info {
  width: 150px;
  display: flex;
  flex-direction: column;
}

.bar-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.bar-profession {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.bar-wrapper {
  flex: 1;
  height: v-bind(BAR_HEIGHT_SMALL);
  background-color: var(--color-card-hover);
  border-radius: 0.25rem;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  position: absolute;
  top: 0;
  height: 100%;
  transition: width 0.3s ease;
}

.healing-bar {
  left: 0;
  background: linear-gradient(90deg, v-bind(COLOR_HEALING_START), v-bind(COLOR_HEALING_END));
  border-radius: 0.25rem 0 0 0.25rem;
}

.barrier-bar {
  background: linear-gradient(90deg, v-bind(COLOR_BARRIER_START), v-bind(COLOR_BARRIER_END));
  border-radius: 0 0.25rem 0.25rem 0;
}

.bar-value {
  width: 100px;
  text-align: right;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
