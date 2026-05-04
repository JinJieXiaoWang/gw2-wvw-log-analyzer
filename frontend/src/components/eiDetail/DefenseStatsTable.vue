<template>
  <div class="defense-stats-table card">
    <div class="table-header">
      <h3 class="table-title">
        <i class="pi pi-shield" />
        防御统计
      </h3>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-player">
              玩家
            </th>
            <th class="col-dmg">
              承受伤害
            </th>
            <th class="col-block">
              格挡
            </th>
            <th class="col-evade">
              闪避
            </th>
            <th class="col-dodge">
              翻滚
            </th>
            <th class="col-invul">
              无敌
            </th>
            <th class="col-miss">
              未命�?            </th>
            <th class="col-barrier">
              屏障
            </th>
            <th class="col-down">
              倒地
            </th>
            <th class="col-death">
              死亡
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
            <td class="col-dmg">
              {{ formatDamage(getDefense(player).damageTaken) }}
            </td>
            <td class="col-block">
              {{ getDefense(player).blockedCount }}
            </td>
            <td class="col-evade">
              {{ getDefense(player).evadedCount }}
            </td>
            <td class="col-dodge">
              {{ getDefense(player).dodgeCount }}
            </td>
            <td class="col-invul">
              {{ getDefense(player).invulnedCount }}
            </td>
            <td class="col-miss">
              {{ getDefense(player).missedCount }}
            </td>
            <td class="col-barrier">
              {{ formatDamage(getDefense(player).damageBarrier) }}
            </td>
            <td class="col-down">
              <span :class="{ danger: getDefense(player).downCount > 0 }">
                {{ getDefense(player).downCount }}
              </span>
            </td>
            <td class="col-death">
              <span :class="{ danger: getDefense(player).deadCount > 0 }">
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

<style scoped lang="css">
.defense-stats-table {
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

.col-dmg,
.col-block,
.col-evade,
.col-dodge,
.col-invul,
.col-miss,
.col-barrier,
.col-down,
.col-death {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}

.danger {
  color: var(--color-error);
}
</style>
