<template>
  <div class="offensive-stats-table card">
    <div class="table-header">
      <h3 class="table-title">
        <i class="pi pi-bolt" />
        进攻统计
      </h3>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-player">
              玩家
            </th>
            <th class="col-crit">
              暴击�?            </th>
            <th class="col-crit-dmg">
              暴击伤害
            </th>
            <th class="col-flank">
              侧身�?            </th>
            <th class="col-glance">
              擦过�?            </th>
            <th class="col-miss">
              未命�?            </th>
            <th class="col-interrupt">
              打断
            </th>
            <th class="col-invul">
              击中无敌
            </th>
            <th class="col-against-down">
              对倒地
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="player in sortedPlayers"
            :key="player.instanceID"
            class="data-row"
            :class="{ selected: selectedPlayerId === player.instanceID }"
            @click="$emit('select-player', player.instanceID)"
          >
            <td class="col-player">
              <div class="player-cell">
                <img
                  :src="getProfIcon(player.profession)"
                  class="player-avatar"
                  alt=""
                >
                <span class="player-name">{{ player.name }}</span>
              </div>
            </td>
            <td class="col-crit">
              {{ formatPercent(getStats(player).criticalRate) }}
            </td>
            <td class="col-crit-dmg">
              {{ formatDamage(getStats(player).criticalDmg) }}
            </td>
            <td class="col-flank">
              {{ formatPercent(getStats(player).flankingRate) }}
            </td>
            <td class="col-glance">
              {{ formatPercent(getStats(player).glanceRate) }}
            </td>
            <td class="col-miss">
              {{ getStats(player).missed }}
            </td>
            <td class="col-interrupt">
              {{ getStats(player).interrupts }}
            </td>
            <td class="col-invul">
              {{ getStats(player).invulned }}
            </td>
            <td class="col-against-down">
              {{ getStats(player).againstDownedCount }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player, PlayerStats } from '@/types/eliteInsights'
import { formatDamage, formatPercent } from '@/types/eliteInsights'
import { getProfessionIconUrl } from '@/utils/profession/professionUtils'

interface Props {
  players: Player[]
  selectedPlayerId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedPlayerId: null
})

defineEmits<{
  (e: 'select-player', id: number): void
}>()

const sortedPlayers = computed(() => {
  return [...props.players].sort((a, b) => {
    const sa = getStats(a).criticalRate || 0
    const sb = getStats(b).criticalRate || 0
    return sb - sa
  })
})

function getStats(player: Player): PlayerStats {
  return player.statsAll?.[0] || {
    wasted: 0, timeWasted: 0, saved: 0, timeSaved: 0,
    stackDist: 0, distToCom: 0, avgBoons: 0, avgActiveBoons: 0,
    avgConditions: 0, avgActiveConditions: 0, swapCount: 0,
    skillCastUptime: 0, skillCastUptimeNoAA: 0, totalDamageCount: 0,
    totalDmg: 0, directDamageCount: 0, directDmg: 0,
    connectedDirectDamageCount: 0, connectedDirectDmg: 0,
    connectedDamageCount: 0, connectedDmg: 0,
    critableDirectDamageCount: 0, criticalRate: 0, criticalDmg: 0,
    flankingRate: 0, againstMovingRate: 0, glanceRate: 0,
    missed: 0, evaded: 0, blocked: 0, interrupts: 0, invulned: 0,
    killed: 0, downed: 0, downContribution: 0,
    connectedPowerCount: 0, connectedPowerAbove90HPCount: 0,
    connectedConditionCount: 0, connectedConditionAbove90HPCount: 0,
    againstDownedCount: 0, againstDownedDamage: 0
  }
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.offensive-stats-table {
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
  color: var(--color-error);
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background-color: var(--color-card-hover);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.data-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.data-row:hover {
  background-color: var(--color-card-hover);
}

.data-row.selected {
  background-color: var(--color-primary-alpha-10);
}

.player-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.player-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.player-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.col-crit,
.col-crit-dmg,
.col-flank,
.col-glance,
.col-miss,
.col-interrupt,
.col-invul,
.col-against-down {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}
</style>
