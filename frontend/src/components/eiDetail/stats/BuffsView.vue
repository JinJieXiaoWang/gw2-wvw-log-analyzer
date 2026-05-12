<template>
  <div class="buffs-view flex flex-col gap-6">
    <!-- 团队增益覆盖 -->
    <div class="buffs-section card bg-neutral-card rounded-xl border border-neutral-border overflow-hidden">
      <div class="section-header flex items-center justify-between p-[1rem 1.25rem] bg-neutral-card-hover">
        <h3 class="section-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
          <i class="pi pi-shield text-primary" />
          团队增益覆盖
        </h3>
      </div>
      <div class="buffs-grid grid grid-cols-[repeat(auto-fit, minmax(300px, 1fr))] gap-4 p-5">
        <BoonsUptimeCard
          v-for="(boonData, index) in playerBoons"
          :key="index"
          :boons-data="boonData.boons"
        />
      </div>
    </div>

    <!-- 增益统计表格 -->
    <div class="buff-table-section card bg-neutral-card rounded-xl border border-neutral-border overflow-hidden">
      <div class="section-header flex items-center justify-between p-[1rem 1.25rem] bg-neutral-card-hover">
        <h3 class="section-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
          <i class="pi pi-list text-primary" />
          增益详细统计
        </h3>
      </div>
      <div class="table-wrapper overflow-x-auto">
        <table class="data-table w-full">
          <thead>
            <tr>
              <th class="col-player p-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider whitespace-nowrap">
                玩家
              </th>
              <th class="col-boon p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
                平均增益
              </th>
              <th class="col-boon-active p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
                活跃增益
              </th>
              <th class="col-condi p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
                平均症状
              </th>
              <th class="col-condi-active p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
                活跃症状
              </th>
              <th class="col-swap p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
                武器切换
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
              <td class="col-boon p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
                {{ formatDecimal(getStats(player).avgBoons) }}
              </td>
              <td class="col-boon-active p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
                {{ formatDecimal(getStats(player).avgActiveBoons) }}
              </td>
              <td class="col-condi p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
                {{ formatDecimal(getStats(player).avgConditions) }}
              </td>
              <td class="col-condi-active p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
                {{ formatDecimal(getStats(player).avgActiveConditions) }}
              </td>
              <td class="col-swap p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
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
import { Colors } from '@/config/designTokens'

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
  return props.players.slice(0, 4).map(player => ({
    name: player.name,
    boons: (player.buffUptimes || []).slice(0, 6).map((buff, idx) => ({
      id: buff.id || idx,
      name: `Buff ${buff.id || idx}`,
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
  const colors = [Colors.palette.green, Colors.palette.blue, Colors.palette.amber, Colors.palette.red, Colors.palette.violet, Colors.palette.cyan]
  return colors[index % colors.length]
}

function formatDecimal(value: number): string {
  return (value || 0).toFixed(1)
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>


