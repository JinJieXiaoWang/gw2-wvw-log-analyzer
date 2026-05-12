<template>
  <div class="support-stats-table card">
    <div class="table-header">
      <h3 class="table-title">
        <i class="pi pi-sparkles" />
        支援统计
      </h3>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-player">
              玩家
            </th>
            <th class="col-cleanse">
              症状清除
            </th>
            <th class="col-cleanse-time">
              清除耗时
            </th>
            <th class="col-strip">
              增益剥离
            </th>
            <th class="col-strip-time">
              剥离耗时
            </th>
            <th class="col-res">
              复活
            </th>
            <th class="col-interrupt">
              打断
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
            <td class="col-cleanse">
              {{ player.support?.[0]?.condiCleanse || 0 }}
            </td>
            <td class="col-cleanse-time">
              -
            </td>
            <td class="col-strip">
              {{ player.support?.[0]?.boonStrips || 0 }}
            </td>
            <td class="col-strip-time">
              -
            </td>
            <td class="col-res">
              -
            </td>
            <td class="col-interrupt">
              {{ getStats(player).interrupts }}
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
  const list = [...props.players]
  return list.sort((a, b) => {
    const sa = (a.support?.[0]?.condiCleanse || 0) + (a.support?.[0]?.boonStrips || 0)
    const sb = (b.support?.[0]?.condiCleanse || 0) + (b.support?.[0]?.boonStrips || 0)
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
.support-stats-table {
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
  color: var(--color-accent);
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

.col-cleanse,
.col-cleanse-time,
.col-strip,
.col-strip-time,
.col-res,
.col-interrupt {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}
</style>
