<template>
  <div class="stats-view">
    <StatsDamageChart
      :players="playersSortedByDmg"
      :active-tab="activeChartTab"
      :total-damage="totalDamage"
      :avg-dps="avgDps"
      :fight-duration="fightDuration"
      @update:active-tab="emit('update:activeChartTab', $event)"
    />

    <!-- 团队统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
      <div class="stat-card damage">
        <div class="stat-icon">
          <i class="pi pi-bolt" />
        </div>
        <div class="stat-info">
          <span class="stat-label">总伤害</span>
          <span class="stat-value">{{ formatLargeNumber(totalDamage) }}</span>
        </div>
      </div>
      <div class="stat-card dps">
        <div class="stat-icon">
          <i class="pi pi-gauge" />
        </div>
        <div class="stat-info">
          <span class="stat-label">平均DPS</span>
          <span class="stat-value">{{ formatLargeNumber(avgDps) }}</span>
        </div>
      </div>
      <div class="stat-card survival">
        <div class="stat-icon">
          <i class="pi pi-heart" />
        </div>
        <div class="stat-info">
          <span class="stat-label">存活玩家</span>
          <span class="stat-value">{{ alivePlayers }}/{{ playersSortedByDmg.length }}</span>
        </div>
      </div>
      <div class="stat-card score">
        <div class="stat-icon">
          <i class="pi pi-trophy" />
        </div>
        <div class="stat-info">
          <span class="stat-label">团队评分</span>
          <span class="stat-value">{{ teamScore }}</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
      <DamageDistributionChart
        :power-damage="totalPowerDamage"
        :condi-damage="totalCondiDamage"
        :breakbar-damage="totalBreakbarDamage"
      />
      <SkillCastChart
        :skills="mockSkills"
        :uptime="78"
        :duration="durationMs || 0"
      />
    </div>

    <StatsPlayerTable
      :players="playersSortedByDmg"
      :sort-by="sortBy"
      :selected-player-id="selectedPlayerId"
      @select-player="emit('select-player', $event)"
      @update:sort-by="emit('update:sortBy', $event)"
    />

    <div
      v-if="selectedPlayer"
      class="player-detail-section card mt-6"
    >
      <PlayerStatsDetail :player="selectedPlayer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { computed } from 'vue'
import DamageDistributionChart from '../charts/DamageDistributionChart.vue'
import SkillCastChart from '../charts/SkillCastChart.vue'
import StatsDamageChart from '../charts/StatsDamageChart.vue'
import PlayerStatsDetail from '../player/PlayerStatsDetail.vue'
import StatsPlayerTable from '../tables/StatsPlayerTable.vue'

const props = defineProps<{
  playersSortedByDmg: Player[]
  selectedPlayerId: number | null
  selectedPlayer: Player | null
  fightDuration: string
  durationMs: number
  sortBy: string
  activeChartTab: string
}>()

const emit = defineEmits(['select-player', 'update:sortBy', 'update:activeChartTab'])

const mockSkills = [
  { id: 1, name: '裁决重击', count: 45 },
  { id: 2, name: '龙魂斩', count: 38 },
  { id: 3, name: '正义之怒', count: 32 },
  { id: 4, name: '守护光环', count: 28 },
  { id: 5, name: '神圣裁决', count: 25 },
  { id: 6, name: '战斗怒吼', count: 22 },
  { id: 7, name: '治愈之光', count: 18 },
  { id: 8, name: '破甲打击', count: 15 },
]

function getPlayerDamage(player: Player): number { return player.dpsAll?.[0]?.damage || 0 }
function getPlayerPowerDamage(player: Player): number { return player.dpsAll?.[0]?.powerDamage || 0 }
function getPlayerCondiDamage(player: Player): number { return player.dpsAll?.[0]?.condiDamage || 0 }

const totalDamage = computed(() => props.playersSortedByDmg.reduce((sum, p) => sum + getPlayerDamage(p), 0))
const totalPowerDamage = computed(() => props.playersSortedByDmg.reduce((sum, p) => sum + getPlayerPowerDamage(p), 0))
const totalCondiDamage = computed(() => props.playersSortedByDmg.reduce((sum, p) => sum + getPlayerCondiDamage(p), 0))
const totalBreakbarDamage = computed(() => props.playersSortedByDmg.reduce((sum, p) => sum + (p.dpsAll?.[0]?.breakbarDamage || 0), 0))
const avgDps = computed(() => {
  const total = props.playersSortedByDmg.reduce((sum, p) => sum + p.dps, 0)
  return Math.round(total / props.playersSortedByDmg.length)
})
const alivePlayers = computed(() => props.playersSortedByDmg.filter(p => p.deaths === 0).length)
const teamScore = computed(() => {
  const total = props.playersSortedByDmg.reduce((sum, p) => sum + p.total_score, 0)
  return Math.round(total / props.playersSortedByDmg.length)
})

function formatLargeNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped lang="css">
.stats-view {
  display: flex;
  flex-direction: column;
}

.damage-chart-section {
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.chart-title i {
  color: var(--color-primary);
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
  background-color: var(--color-primary);
  color: white;
}

.chart-container {
  display: flex;
  gap: 2rem;
}

.chart-placeholder {
  display: flex;
  gap: 2rem;
  flex: 1;
}

.chart-content {
  flex: 1;
}

.damage-bars {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.damage-bar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bar-label {
  width: 140px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: var(--color-card-hover);
  color: var(--color-text-secondary);
}

.rank.gold {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: white;
}

.rank.silver {
  background: linear-gradient(135deg, #9ca3af, #d1d5db);
  color: white;
}

.rank.bronze {
  background: linear-gradient(135deg, #cd7f32, #d4956a);
  color: white;
}

.name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.bar-container {
  flex: 1;
  height: 24px;
  background-color: var(--color-bg);
  border-radius: 0.25rem;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 0.25rem;
  transition: width 0.5s ease;
}

.bar-value {
  width: 100px;
  text-align: right;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.chart-summary {
  width: 180px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-left: 1.5rem;
  border-left: 1px solid var(--color-border);
}

.summary-item {
  display: flex;
  justify-content: space-between;
}

.summary-item .label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.summary-item .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.stat-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
}

.stat-card.damage .stat-icon {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.stat-card.dps .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
}

.stat-card.survival .stat-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.stat-card.score .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #eab308);
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.player-table-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.table-title i {
  color: var(--color-primary);
}

.table-controls {
  display: flex;
  gap: 0.75rem;
}

.sort-select {
  display: flex;
  align-items: center;
}

.sort-dropdown {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.875rem;
}

.table-wrapper {
  overflow-x: auto;
}

.player-table {
  width: 100%;
  border-collapse: collapse;
}

.player-table th,
.player-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.player-table th {
  background-color: var(--color-card-hover);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.player-row:hover {
  background-color: var(--color-card-hover);
}

.player-row.selected {
  background-color: var(--color-primary);
}

.player-row.selected td {
  color: white;
}

.player-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.player-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.player-info {
  display: flex;
  flex-direction: column;
}

.player-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.player-account {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
}

.commander-icon {
  color: #f59e0b;
}

.profession-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

.score-value,
.damage-value,
.dps-value,
.power-value,
.condi-value,
.cc-value,
.cleanses-value,
.strips-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.downs-value,
.deaths-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.downs-value.danger,
.deaths-value.danger {
  color: var(--color-error);
}

.weapons-value {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.player-detail-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.mb-6 {
  margin-bottom: 1.5rem;
}
</style>
