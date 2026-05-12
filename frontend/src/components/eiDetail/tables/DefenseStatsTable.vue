<template>
  <div class="defense-stats-table card bg-neutral-card rounded-xl overflow-hidden">
    <div class="table-header flex items-center justify-between p-[1rem 1.25rem] bg-neutral-card-hover">
      <h3 class="table-title flex items-center gap-2 text-base font-semibold text-neutral-text m-0">
        <i class="pi pi-shield text-primary" />
        防御统计
      </h3>
    </div>
    <div class="table-wrapper overflow-x-auto">
      <table class="data-table w-full">
        <thead>
          <tr>
            <th class="col-player p-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider whitespace-nowrap">
              玩家
            </th>
            <th class="col-dmg p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              承受伤害
            </th>
            <th class="col-block p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              格挡
            </th>
            <th class="col-evade p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              闪避
            </th>
            <th class="col-dodge p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              翻滚
            </th>
            <th class="col-invul p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              无敌
            </th>
            <th class="col-miss p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              未命�?
            </th>
            <th class="col-barrier p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              屏障
            </th>
            <th class="col-down p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              倒地
            </th>
            <th class="col-death p-3 px-4 border-b border-neutral-border bg-neutral-card-hover text-sm font-semibold text-neutral-text uppercase tracking-wider whitespace-nowrap text-center">
              死亡
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
            <td class="col-dmg p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ formatDamage(getDefense(player).damageTaken) }}
            </td>
            <td class="col-block p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getDefense(player).blockedCount }}
            </td>
            <td class="col-evade p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getDefense(player).evadedCount }}
            </td>
            <td class="col-dodge p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getDefense(player).dodgeCount }}
            </td>
            <td class="col-invul p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getDefense(player).invulnedCount }}
            </td>
            <td class="col-miss p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ getDefense(player).missedCount }}
            </td>
            <td class="col-barrier p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              {{ formatDamage(getDefense(player).damageBarrier) }}
            </td>
            <td class="col-down p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              <span class="text-status-error" :class="{ danger: getDefense(player).downCount > 0 }">
                {{ getDefense(player).downCount }}
              </span>
            </td>
            <td class="col-death p-3 px-4 border-b border-neutral-border text-sm font-semibold text-neutral-text text-center">
              <span class="text-status-error" :class="{ danger: getDefense(player).deadCount > 0 }">
                {{ getDefense(player).deadCount }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player, PlayerDefense } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'
import { getProfessionIconUrl } from '@/utils/profession/professionUtils'

interface Props {
  players: Player[]
  selectedPlayerId?: number | null
  sortBy?: 'damageTaken' | 'dodgeCount' | 'downCount'
}

const props = withDefaults(defineProps<Props>(), {
  selectedPlayerId: null,
  sortBy: 'damageTaken'
})

defineEmits<{
  (e: 'select-player', id: number): void
}>()

const sortedPlayers = computed(() => {
  const list = [...props.players]
  const key = props.sortBy
  return list.sort((a, b) => {
    const da = getDefense(a)[key] || 0
    const db = getDefense(b)[key] || 0
    return db - da
  })
})

function getDefense(player: Player): PlayerDefense {
  return player.defenses?.[0] || {
    damageTaken: 0,
    downedDamageTaken: 0,
    breakbarDamageTaken: 0,
    blockedCount: 0,
    evadedCount: 0,
    missedCount: 0,
    dodgeCount: 0,
    invulnedCount: 0,
    damageBarrier: 0,
    interruptedCount: 0,
    downCount: player.downs || 0,
    downDuration: 0,
    deadCount: player.deaths || 0,
    deadDuration: 0,
    dcCount: 0,
    dcDuration: 0,
    boonStrips: 0,
    boonStripsTime: 0,
    conditionCleanses: 0,
    conditionCleansesTime: 0
  }
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}
</script>


