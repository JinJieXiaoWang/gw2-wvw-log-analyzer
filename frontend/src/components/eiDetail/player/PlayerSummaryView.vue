<template>
  <div class="player-summary-view">
    <PlayerSummarySelector
      :players="players"
      :selected-id="selectedId"
      @select-player="selectPlayer"
    />

    <div
      v-if="selectedPlayer"
      class="player-detail card"
    >
      <PlayerSummaryDetailHeader :player="selectedPlayer" />

      <div class="detail-stats">
        <PlayerSummaryDamageStats :dps="getDps(selectedPlayer)" />
        <PlayerSummaryDefenseStats :defense="getDefense(selectedPlayer)" />
        <PlayerSummaryPerformanceStats :stats="getStats(selectedPlayer)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player, PlayerDefense, PlayerDps, PlayerStats } from '@/types/eliteInsights'
import { computed, ref } from 'vue'
import PlayerSummaryDamageStats from './PlayerSummaryDamageStats.vue'
import PlayerSummaryDefenseStats from './PlayerSummaryDefenseStats.vue'
import PlayerSummaryDetailHeader from './PlayerSummaryDetailHeader.vue'
import PlayerSummaryPerformanceStats from './PlayerSummaryPerformanceStats.vue'
import PlayerSummarySelector from './PlayerSummarySelector.vue'

interface Props {
  players: Player[]
  selectedPlayerId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedPlayerId: null
})

const emit = defineEmits<{
  (e: 'select-player', id: number | null): void
}>()

const selectedId = ref<number | null>(props.selectedPlayerId)

const selectedPlayer = computed(() => {
  return props.players.find(p => p.instanceID === selectedId.value) || null
})

function selectPlayer(id: number) {
  selectedId.value = id
  emit('select-player', id)
}

function getDps(player: Player): PlayerDps {
  return player.dpsAll?.[0] || {
    dps: 0, damage: 0, condiDps: 0, condiDamage: 0,
    powerDps: 0, powerDamage: 0, breakbarDamage: 0,
    actorDps: 0, actorDamage: 0, actorCondiDps: 0,
    actorCondiDamage: 0, actorPowerDps: 0, actorPowerDamage: 0,
    actorBreakbarDamage: 0
  }
}

function getDefense(player: Player): PlayerDefense {
  return player.defenses?.[0] || {
    damageTaken: 0, downedDamageTaken: 0, breakbarDamageTaken: 0,
    blockedCount: 0, evadedCount: 0, missedCount: 0, dodgeCount: 0,
    invulnedCount: 0, damageBarrier: 0, interruptedCount: 0,
    downCount: 0, downDuration: 0, deadCount: 0, deadDuration: 0,
    dcCount: 0, dcDuration: 0, boonStrips: 0, boonStripsTime: 0,
    conditionCleanses: 0, conditionCleansesTime: 0
  }
}

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
</script>

<style scoped lang="css">
.player-summary-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.player-detail {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
  padding: 1.25rem;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
</style>
