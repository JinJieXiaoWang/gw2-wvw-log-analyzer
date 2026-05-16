<template>
  <div class="player-stats-table">
    <div class="table-header">
      <h3 class="table-title">
        <i class="pi pi-list" />
        玩家统计
      </h3>
      <div class="table-tools">
        <PlayerStatsSortBar
          v-model="currentSort"
          :sort-options="sortOptions"
        />
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th class="rank-col">#</th>
            <th class="player-col">玩家</th>
            <th class="prof-col">职业</th>
            <th class="score-col">评分</th>
            <th class="dmg-col">总伤害</th>
            <th class="dps-col">DPS</th>
            <th class="power-col">直伤</th>
            <th class="condi-col">症状</th>
            <th class="cc-col">CC</th>
            <th class="down-col">倒地</th>
            <th class="death-col">死亡</th>
            <th class="actions-col" />
          </tr>
        </thead>
        <tbody>
          <PlayerStatsTableRow
            v-for="(player, index) in sortedPlayers"
            :key="player.instanceID"
            :player="player"
            :index="index"
            :selected-id="selectedId"
            @select-player="$emit('select-player', $event)"
          />
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PLAYER_STATS_SORT_OPTIONS } from '@/constants/dictValues'
import PlayerStatsSortBar from './PlayerStatsSortBar.vue'
import PlayerStatsTableRow from './PlayerStatsTableRow.vue'
import type { Player } from '@/types/eliteInsights'
import { computed, onMounted, ref } from 'vue'
import { useProfession } from '@/composables/useProfession'

interface Props {
  players: Player[]
  selectedId: number | null
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'select-player', instanceId: number): void
}>()

const { loadProfessionData } = useProfession()

type SortKey = 'dps' | 'score' | 'dmg' | 'name'

const currentSort = ref<SortKey>('dps')

const sortOptions = PLAYER_STATS_SORT_OPTIONS.map(o => ({ key: o.key as SortKey, label: o.label }))

const sortedPlayers = computed(() => {
  const list = [...props.players]
  switch (currentSort.value) {
    case 'dps':
      return list.sort((a, b) => b.dps - a.dps)
    case 'score':
      return list.sort((a, b) => b.total_score - a.total_score)
    case 'dmg':
      return list.sort((a, b) => getPlayerDamage(b) - getPlayerDamage(a))
    case 'name':
      return list.sort((a, b) => a.name.localeCompare(b.name))
    default:
      return list
  }
})

function getPlayerDamage(player: Player): number {
  return player.dpsAll?.[0]?.damage || 0
}

onMounted(() => {
  loadProfessionData().catch(error => {
    console.error('[PlayerStatsTable] 加载职业数据失败:', error)
  })
})
</script>

<style scoped lang="css">
.player-stats-table {
  background-color: var(--color-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-card);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.table-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.table-tools {
  display: flex;
  gap: var(--spacing-md);
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  padding: var(--spacing-md);
  text-align: left;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--color-border);
}

.rank-col { width: 48px; }
.player-col { min-width: 200px; }
.prof-col { width: 100px; }
.score-col, .dps-col, .dmg-col, .power-col, .condi-col, .cc-col, .down-col, .death-col { text-align: right; }
.actions-col { width: 48px; text-align: center; }

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  .table-tools { flex-wrap: wrap; }
}
</style>
