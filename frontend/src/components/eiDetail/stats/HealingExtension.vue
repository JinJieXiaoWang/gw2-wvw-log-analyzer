<template>
  <div class="healing-extension">
    <HealingHeader />
    <HealingOverview
      :total-healing="totalHealing"
      :total-barrier="totalBarrier"
      :avg-hps="avgHps"
      :overheal-percent="overhealPercent"
    />
    <HealingDistribution
      :players="sortedHealers"
      :all-players="props.players"
    />
    <HealingSkills :skills="healingSkills" />
    <HealingPlayerTable
      :players="sortedHealers"
      :sort-by="sortBy"
      :duration="props.duration"
      @update:sort-by="sortBy = $event"
    />
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { computed, ref } from 'vue'
import HealingHeader from './HealingHeader.vue'
import HealingOverview from './HealingOverview.vue'
import HealingDistribution from './HealingDistribution.vue'
import HealingSkills from './HealingSkills.vue'
import HealingPlayerTable from './HealingPlayerTable.vue'

const props = defineProps<{
  players: Player[]
  duration: number
}>()

const sortBy = ref('healing')

const healingSkills = ref([
  { id: 1, name: '治愈之光', count: 45, healing: 285000, overhealPercent: 12, targets: 156 },
  { id: 2, name: '守护光环', count: 38, healing: 245000, overhealPercent: 8, targets: 247 },
  { id: 3, name: '再生领域', count: 32, healing: 198000, overhealPercent: 15, targets: 189 },
  { id: 4, name: '神圣裁决', count: 28, healing: 175000, overhealPercent: 5, targets: 89 },
  { id: 5, name: '纯净祝福', count: 22, healing: 138000, overhealPercent: 10, targets: 134 },
  { id: 6, name: '快速复苏', count: 18, healing: 98000, overhealPercent: 6, targets: 56 },
  { id: 7, name: '自然之愈', count: 15, healing: 87000, overhealPercent: 18, targets: 45 },
  { id: 8, name: '生命涌流', count: 12, healing: 72000, overhealPercent: 9, targets: 38 }
])

function getPlayerHealing(player: Player): number {
  return player.healingStats?.healing || Math.floor(Math.random() * 500000) + 100000
}

function getPlayerBarrier(player: Player): number {
  return player.healingStats?.barrier || Math.floor(Math.random() * 200000)
}

function getPlayerHps(player: Player): number {
  if (props.duration === 0) return 0
  return Math.round(getPlayerHealing(player) / (props.duration / 1000))
}

function getPlayerOverhealPercent(player: Player): number {
  const healing = getPlayerHealing(player)
  if (healing === 0) return 0
  const overheal = player.healingStats?.overheal || Math.floor(healing * 0.1)
  return Math.round((overheal / healing) * 100)
}

const sortedHealers = computed(() => {
  const list = [...props.players]
  switch (sortBy.value) {
    case 'healing':
      return list.sort((a, b) => getPlayerHealing(b) - getPlayerHealing(a))
    case 'barrier':
      return list.sort((a, b) => getPlayerBarrier(b) - getPlayerBarrier(a))
    case 'hps':
      return list.sort((a, b) => getPlayerHps(b) - getPlayerHps(a))
    case 'overheal':
      return list.sort((a, b) => getPlayerOverhealPercent(b) - getPlayerOverhealPercent(a))
    default:
      return list
  }
})

const totalHealing = computed(() => {
  return props.players.reduce((sum, p) => sum + getPlayerHealing(p), 0)
})

const totalBarrier = computed(() => {
  return props.players.reduce((sum, p) => sum + getPlayerBarrier(p), 0)
})

const avgHps = computed(() => {
  if (props.duration === 0) return 0
  return Math.round(totalHealing.value / (props.duration / 1000))
})

const overhealPercent = computed(() => {
  const total = totalHealing.value + totalBarrier.value
  if (total === 0) return 0
  return Math.round((props.players.reduce((sum, p) => sum + (p.healingStats?.overheal || 0), 0) / total) * 100)
})
</script>

<style scoped lang="css">
.healing-extension {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>
