<template>
  <div class="buffs-view">
    <!-- 团队增益覆盖 -->
    <div class="buffs-section card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="pi pi-shield" />
          {{ SECTION_TEAM_BUFF_COVERAGE }}
        </h3>
      </div>
      <div class="buffs-grid">
        <BoonsUptimeCard
          v-for="(boonData, index) in playerBoons"
          :key="index"
          :boons-data="boonData.boons"
        />
      </div>
    </div>

    <!-- 增益统计表格 -->
    <div class="buff-table-section card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="pi pi-list" />
          {{ SECTION_BUFF_DETAIL_STATS }}
        </h3>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-player">
                {{ TABLE_HEADER_PLAYER }}
              </th>
              <th class="col-boon">
                {{ LABEL_AVG_BOON }}
              </th>
              <th class="col-boon-active">
                {{ LABEL_ACTIVE_BOON }}
              </th>
              <th class="col-condi">
                {{ LABEL_AVG_CONDITION }}
              </th>
              <th class="col-condi-active">
                {{ LABEL_ACTIVE_CONDITION }}
              </th>
              <th class="col-swap">
                {{ LABEL_WEAPON_SWAP }}
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
              <td class="col-boon">
                {{ formatDecimal(getStats(player).avgBoons) }}
              </td>
              <td class="col-boon-active">
                {{ formatDecimal(getStats(player).avgActiveBoons) }}
              </td>
              <td class="col-condi">
                {{ formatDecimal(getStats(player).avgConditions) }}
              </td>
              <td class="col-condi-active">
                {{ formatDecimal(getStats(player).avgActiveConditions) }}
              </td>
              <td class="col-swap">
                {{ getStats(player).swapCount }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player, PlayerStats } from '@/types/eliteInsights'
import { getProfessionIconUrl } from '@/utils/profession/professionUtils'
import BoonsUptimeCard from '../charts/BoonsUptimeCard.vue'
import {
  SECTION_TEAM_BUFF_COVERAGE,
  SECTION_BUFF_DETAIL_STATS,
  TABLE_HEADER_PLAYER,
  LABEL_AVG_BOON,
  LABEL_ACTIVE_BOON,
  LABEL_AVG_CONDITION,
  LABEL_ACTIVE_CONDITION,
  LABEL_WEAPON_SWAP,
  LABEL_BUFF_PREFIX,
} from '@/constants/eiLabels'
import { BOON_COLORS } from '@/constants/colors'
import {
  PLAYER_BOON_DISPLAY_COUNT,
  BUFF_UPTIME_DISPLAY_COUNT,
  DECIMAL_PLACES_1,
} from '@/constants/thresholds'

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
    const sa = getStats(a).avgBoons || 0
    const sb = getStats(b).avgBoons || 0
    return sb - sa
  })
})

const playerBoons = computed(() => {
  return props.players.slice(0, PLAYER_BOON_DISPLAY_COUNT).map(player => ({
    name: player.name,
    boons: (player.buffUptimes || []).slice(0, BUFF_UPTIME_DISPLAY_COUNT).map((buff, idx) => ({
      id: buff.id || idx,
      name: `${LABEL_BUFF_PREFIX} ${buff.id || idx}`,
      uptime: Math.round(buff.uptime || 0),
      applied: buff.buffData?.[0]?.buffApplied || 0,
      wasted: buff.buffData?.[0]?.wasted || 0,
      color: getBoonColor(idx)
    }))
  }))
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

function getBoonColor(index: number): string {
  return BOON_COLORS[index % BOON_COLORS.length]
}

function formatDecimal(value: number): string {
  return (value || 0).toFixed(DECIMAL_PLACES_1)
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>

<style scoped lang="css">
.buffs-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.buffs-section,
.buff-table-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
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
  color: var(--color-primary);
}

.buffs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1.25rem;
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

.col-boon,
.col-boon-active,
.col-condi,
.col-condi-active,
.col-swap {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}
</style>
