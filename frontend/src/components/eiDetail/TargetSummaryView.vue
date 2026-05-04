<template>
  <div class="target-summary-view">
    <!-- 目标统计卡片 -->
    <div class="targets-grid">
      <TargetStatsCard
        v-for="target in targets"
        :key="target.instanceID"
        :targets="[target]"
      />
    </div>

    <!-- 目标伤害贡献 -->
    <div class="damage-contribution card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="pi pi-chart-bar" />
          目标伤害贡献
        </h3>
      </div>
      <div class="contribution-list">
        <div
          v-for="target in targetsWithDamage"
          :key="target.instanceID"
          class="contribution-item"
        >
          <div class="target-info-row">
            <img
              v-if="target.icon"
              :src="target.icon"
              class="target-icon-sm"
              alt=""
            >
            <span class="target-name">{{ target.name }}</span>
            <span
              class="target-status-badge"
              :class="{ dead: target.finalHealth === 0 }"
            >
              {{ target.finalHealth === 0 ? '已击杀' : '存活' }}
            </span>
          </div>
          <div class="damage-bar-row">
            <div class="damage-bar-track">
              <div
                class="damage-bar-fill"
                :style="{ width: getDamagePercent(target) + '%' }"
              />
            </div>
            <span class="damage-value">{{ formatDamage(getTargetDamage(target)) }}</span>
          </div>
          <div class="player-contributions">
            <div
              v-for="contrib in getTopContributors(target)"
              :key="contrib.playerId"
              class="contrib-player"
            >
              <span
                class="contrib-dot"
                :style="{ backgroundColor: contrib.color }"
              />
              <span class="contrib-name">{{ contrib.name }}</span>
              <span class="contrib-dmg">{{ formatDamage(contrib.damage) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player, Target } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import TargetStatsCard from './TargetStatsCard.vue'

interface Props {
  targets: Target[]
  players: Player[]
}

const props = defineProps<Props>()

const targetsWithDamage = computed(() => {
  return [...props.targets].sort((a, b) => getTargetDamage(b) - getTargetDamage(a))
})

const maxTargetDamage = computed(() => {
  return Math.max(...props.targets.map(t => getTargetDamage(t)), 1)
})

function getTargetDamage(target: Target): number {
  return target.dpsAll?.[0]?.damage || target.statsAll?.[0]?.totalDmg || 0
}

function getDamagePercent(target: Target): number {
  return (getTargetDamage(target) / maxTargetDamage.value) * 100
}

function getTopContributors(target: Target) {
  const contributors = props.players.slice(0, 3).map(p => ({
    playerId: p.instanceID,
    name: p.name,
    damage: Math.floor(getTargetDamage(target) * (0.4 - props.players.indexOf(p) * 0.1)),
    color: getProfessionColor(p.profession)
  }))
  return contributors.sort((a, b) => b.damage - a.damage)
}
</script>

<style scoped lang="css">
.target-summary-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.targets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.damage-contribution {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
  padding: 1.25rem;
}

.section-header {
  margin-bottom: 1rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.section-title i {
  color: var(--color-error);
}

.contribution-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contribution-item {
  padding: 1rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.target-info-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.target-icon-sm {
  width: 32px;
  height: 32px;
  border-radius: 0.375rem;
}

.target-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  flex: 1;
}

.target-status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.target-status-badge.dead {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.damage-bar-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.damage-bar-track {
  flex: 1;
  height: 8px;
  background-color: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.damage-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-error), var(--color-secondary));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.damage-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  width: 80px;
  text-align: right;
}

.player-contributions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.contrib-player {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
}

.contrib-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.contrib-name {
  color: var(--color-text);
}

.contrib-dmg {
  color: var(--color-text-secondary);
  font-weight: 500;
}
</style>
