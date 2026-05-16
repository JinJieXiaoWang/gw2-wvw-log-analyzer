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

    <StatsOverview
      :total-damage="totalDamage"
      :avg-dps="avgDps"
      :alive-players="alivePlayers"
      :total-players="playersSortedByDmg.length"
      :team-score="teamScore"
    />

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
import StatsOverview from './StatsOverview.vue'

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
</script>

<style scoped lang="css">
.stats-view {
  display: flex;
  flex-direction: column;
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
</style>
