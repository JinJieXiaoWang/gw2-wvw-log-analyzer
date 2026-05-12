<template>
  <div class="offensive-stats-table card bg-neutral-card rounded-xl overflow-hidden">
    <div class="table-header flex items-center justify-between p-[1rem 1.25rem] bg-neutral-card-hover">
      <h3 class="table-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
        <i class="pi pi-bolt text-status-error" />
        进攻统计
      </h3>
    </div>
    <div class="table-wrapper overflow-x-auto">
      <table class="data-table w-full">
        <thead>
          <tr>
            <th class="col-player p-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider whitespace-nowrap">
              玩家
            </th>
            <th class="col-crit p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              暴击�?
            </th>
            <th class="col-crit-dmg p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              暴击伤害
            </th>
            <th class="col-flank p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              侧身�?
            </th>
            <th class="col-glance p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              擦过�?
            </th>
            <th class="col-miss p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              未命�?
            </th>
            <th class="col-interrupt p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              打断
            </th>
            <th class="col-invul p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              击中无敌
            </th>
            <th class="col-against-down p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              对倒地
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="player in sortedPlayers"
            :key="player.instanceID"
            class="data-row cursor-pointer hover:bg-neutral-card-hover"
            :class="{ 'bg-primary/10': selectedPlayerId === player.instanceID }"
            @click="$emit('select-player', player.instanceID)"
          >
            <td class="col-player p-3 px-4 text-left border-b border-neutral-border">
              <div class="player-cell flex items-center gap-2">
                <img
                  :src="getProfIcon(player.profession)"
                  class="player-avatar w-6 h-6 rounded-full"
                  alt=""
                >
                <span class="player-name text-sm font-medium text-neutral-text">{{ player.name }}</span>
              </div>
            </td>
            <td class="col-crit p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ formatPercent(getStats(player).criticalRate) }}
            </td>
            <td class="col-crit-dmg p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ formatDamage(getStats(player).criticalDmg) }}
            </td>
            <td class="col-flank p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ formatPercent(getStats(player).flankingRate) }}
            </td>
            <td class="col-glance p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ formatPercent(getStats(player).glanceRate) }}
            </td>
            <td class="col-miss p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getStats(player).missed }}
            </td>
            <td class="col-interrupt p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getStats(player).interrupts }}
            </td>
            <td class="col-invul p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getStats(player).invulned }}
            </td>
            <td class="col-against-down p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
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


