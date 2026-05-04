<template>
  <div class="player-ranking">
    <div class="ranking-header">
      <h3 class="ranking-title">
        <i class="pi pi-trophy" />
        玩家表现
      </h3>
      <div class="sort-tabs">
        <button
          v-for="tab in sortTabs"
          :key="tab.key"
          class="sort-tab"
          :class="{ active: currentSort === tab.key }"
          @click="setSort(tab.key)"
        >
          <i :class="tab.icon" />
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="ranking-table-container">
      <table class="ranking-table">
        <thead>
          <tr>
            <th class="col-rank">
              #
            </th>
            <th class="col-player">
              玩家
            </th>
            <th class="col-prof">
              职业
            </th>
            <th class="col-damage">
              伤害
            </th>
            <th class="col-dps">
              DPS
            </th>
            <th class="col-crit">
              暴击
            </th>
            <th class="col-taken">
              承伤
            </th>
            <th class="col-down">
              倒地
            </th>
            <th class="col-cleanses">
              清症
            </th>
            <th class="col-group">
              小队
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(player, index) in sortedPlayers"
            :key="player.playerId"
            class="player-row"
            :class="{ commander: player.hasCommanderTag }"
            @click="handleSelectPlayer(player.playerId)"
          >
            <td class="col-rank">
              <span
                class="rank-badge"
                :class="getRankClass(index)"
              >
                {{ index + 1 }}
              </span>
            </td>
            <td class="col-player">
              <div class="player-info">
                <img
                  :src="getProfIcon(player.profession)"
                  :alt="player.profession"
                  class="prof-icon-sm"
                >
                <div class="player-names">
                  <span class="char-name">
                    {{ player.characterName }}
                    <i
                      v-if="player.hasCommanderTag"
                      class="pi pi-star-fill commander-icon"
                      title="指挥官"
                    />
                  </span>
                  <span class="account-name">{{ player.account || '-' }}</span>
                </div>
              </div>
            </td>
            <td class="col-prof">
              <span
                class="prof-badge"
                :style="{ backgroundColor: getProfColor(player.profession) + '20', color: getProfColor(player.profession) }"
              >
                {{ player.profession }}
              </span>
            </td>
            <td class="col-damage">
              <div class="damage-bar">
                <div class="damage-value">
                  {{ formatNumber(player.damage) }}
                </div>
                <div class="damage-bar-track">
                  <div
                    class="damage-bar-fill"
                    :style="{ width: getDamagePercent(player.damage) + '%' }"
                  />
                </div>
              </div>
            </td>
            <td class="col-dps">
              {{ formatNumber(player.dps) }}
            </td>
            <td class="col-crit">
              <span
                class="crit-badge"
                :class="getCritClass(player.criticalRate)"
              >
                {{ player.criticalRate.toFixed(1) }}%
              </span>
            </td>
            <td class="col-taken">
              {{ formatNumber(player.damageTaken) }}
            </td>
            <td class="col-down">
              <span :class="{ 'text-danger': player.downCount > 0 }">
                {{ player.downCount }}
              </span>
            </td>
            <td class="col-cleanses">
              {{ player.condiCleanse }}
            </td>
            <td class="col-group">
              <span class="group-badge">G{{ player.groupId }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { getProfessionIconUrl, getProfessionColor } from '@/utils/profession/professionUtils'
import type { WvwPlayerSummary } from '@/services/combat/wvwReportService'

interface Props {
  players: WvwPlayerSummary[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'select-player', playerId: number): void
}>()

function handleSelectPlayer(playerId: number) {
  emit('select-player', playerId)
}

const currentSort = ref('damage')

const sortTabs = [
  { key: 'damage', label: '伤害', icon: 'pi pi-bolt' },
  { key: 'dps', label: 'DPS', icon: 'pi pi-chart-line' },
  { key: 'taken', label: '承伤', icon: 'pi pi-shield' },
  { key: 'downs', label: '倒地', icon: 'pi pi-angle-double-down' },
  { key: 'support', label: '支援', icon: 'pi pi-heart' },
]

const sortedPlayers = computed(() => {
  const sortKey = currentSort.value as keyof WvwPlayerSummary
  return [...props.players].sort((a, b) => {
    const aVal = (a[sortKey] as number) || 0
    const bVal = (b[sortKey] as number) || 0
    return bVal - aVal
  })
})

const maxDamage = computed(() => {
  return Math.max(...props.players.map(p => p.damage), 1)
})

function setSort(key: string) {
  currentSort.value = key
}

function getRankClass(index: number): string {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}

function getProfColor(prof: string): string {
  return getProfessionColor(prof) || '#888'
}

function formatNumber(n: number | undefined | null): string {
  if (n === undefined || n === null || isNaN(n)) return '-'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

function getDamagePercent(damage: number): number {
  return Math.min(100, (damage / maxDamage.value) * 100)
}

function getCritClass(rate: number): string {
  if (rate >= 70) return 'high'
  if (rate >= 40) return 'medium'
  return 'low'
}
</script>

<style scoped>
.player-ranking {
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.ranking-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--surface-border);
  flex-wrap: wrap;
  gap: 0.75rem;
}

.ranking-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.ranking-title i {
  color: #f59e0b;
}

.sort-tabs {
  display: flex;
  gap: 0.25rem;
}

.sort-tab {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--text-color-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.sort-tab:hover {
  background: var(--surface-hover);
}

.sort-tab.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.ranking-table-container {
  overflow-x: auto;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.ranking-table th {
  padding: 0.75rem 0.625rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  background: var(--surface-hover);
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 1;
}

.ranking-table th:first-child {
  padding-left: 1.25rem;
}

.ranking-table th:last-child {
  padding-right: 1.25rem;
}

.ranking-table td {
  padding: 0.625rem;
  border-bottom: 1px solid var(--surface-border);
  vertical-align: middle;
  white-space: nowrap;
}

.ranking-table td:first-child {
  padding-left: 1.25rem;
}

.ranking-table td:last-child {
  padding-right: 1.25rem;
}

.player-row {
  cursor: pointer;
  transition: background 0.15s;
}

.player-row:hover {
  background: var(--surface-hover);
}

.player-row.commander {
  background: rgba(245, 158, 11, 0.05);
}

.player-row.commander:hover {
  background: rgba(245, 158, 11, 0.1);
}

.col-rank {
  width: 40px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-color-secondary);
  background: var(--surface-hover);
}

.rank-badge.gold {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
}

.rank-badge.silver {
  background: linear-gradient(135deg, #e5e7eb, #9ca3af);
  color: white;
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #fdba74, #f97316);
  color: white;
}

.col-player {
  min-width: 180px;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.prof-icon-sm {
  width: 28px;
  height: 28px;
  border-radius: 0.25rem;
  object-fit: contain;
}

.player-names {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.char-name {
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.commander-icon {
  color: #f59e0b;
  font-size: 0.75rem;
}

.account-name {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.col-prof {
  width: 80px;
}

.prof-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.col-damage {
  min-width: 140px;
}

.damage-bar {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.damage-value {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.8125rem;
}

.damage-bar-track {
  height: 4px;
  background: var(--surface-hover);
  border-radius: 2px;
  overflow: hidden;
}

.damage-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #ef4444, #f97316);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.col-dps {
  width: 70px;
  font-weight: 600;
  color: var(--text-color);
}

.col-crit {
  width: 60px;
}

.crit-badge {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.crit-badge.high {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.crit-badge.medium {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.crit-badge.low {
  background: rgba(156, 163, 175, 0.15);
  color: #9ca3af;
}

.col-taken {
  width: 70px;
  color: var(--text-color-secondary);
}

.col-down {
  width: 50px;
}

.text-danger {
  color: #ef4444;
  font-weight: 600;
}

.col-cleanses {
  width: 60px;
  color: var(--text-color-secondary);
}

.col-group {
  width: 50px;
}

.group-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.125rem 0.375rem;
  background: var(--surface-hover);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color-secondary);
}
</style>
