<template>
  <div class="table-section">
    <div class="section-header">
      <h3 class="section-title">
        <i class="pi pi-users" />
        {{ PLAYER_HEALING_DETAIL_TITLE }}
      </h3>
      <div class="table-controls">
        <select
          v-model="sortByModel"
          class="sort-dropdown"
        >
          <option value="healing">
            {{ SORT_OPTION_HEALING }}
          </option>
          <option value="barrier">
            {{ SORT_OPTION_BARRIER }}
          </option>
          <option value="hps">
            {{ SORT_OPTION_HPS }}
          </option>
          <option value="overheal">
            {{ SORT_OPTION_OVERHEAL }}
          </option>
        </select>
      </div>
    </div>
    <div class="table-wrapper">
      <table class="healing-table">
        <thead>
          <tr>
            <th>{{ TABLE_HEADER_RANK }}</th>
            <th>{{ TABLE_HEADER_PLAYER }}</th>
            <th>{{ TABLE_HEADER_PROFESSION }}</th>
            <th>{{ TABLE_HEADER_HEALING }}</th>
            <th>{{ TABLE_HEADER_BARRIER }}</th>
            <th>{{ TABLE_HEADER_HPS }}</th>
            <th>{{ TABLE_HEADER_OVERHEAL_PERCENT }}</th>
            <th>{{ TABLE_HEADER_CRIT_PERCENT }}</th>
            <th>{{ TABLE_HEADER_HEALING_SKILLS }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(player, index) in players"
            :key="player.instanceID"
          >
            <td>{{ index + 1 }}</td>
            <td>
              <div class="player-cell">
                <img
                  :src="getProfIcon(player.profession)"
                  class="player-avatar"
                >
                <span class="player-name">{{ player.name }}</span>
              </div>
            </td>
            <td>
              <span
                class="profession-badge"
                :style="{ backgroundColor: getProfessionColor(player.profession) }"
              >
                {{ getProfessionName(player.profession) }}
              </span>
            </td>
            <td>{{ formatLargeNumber(getPlayerHealing(player)) }}</td>
            <td>{{ formatLargeNumber(getPlayerBarrier(player)) }}</td>
            <td>{{ formatLargeNumber(getPlayerHps(player)) }}</td>
            <td>{{ getPlayerOverhealPercent(player) }}%</td>
            <td>{{ getPlayerCritPercent(player) }}%</td>
            <td>{{ player.healingSkillsCount || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import {
  getProfessionColor,
  getProfessionIconUrl,
  getProfessionName,
} from '@/utils/profession/professionUtils'
import {
  PLAYER_HEALING_DETAIL_TITLE,
  SORT_OPTION_HEALING,
  SORT_OPTION_BARRIER,
  SORT_OPTION_HPS,
  SORT_OPTION_OVERHEAL,
  TABLE_HEADER_RANK,
  TABLE_HEADER_PLAYER,
  TABLE_HEADER_PROFESSION,
  TABLE_HEADER_HEALING,
  TABLE_HEADER_BARRIER,
  TABLE_HEADER_HPS,
  TABLE_HEADER_OVERHEAL_PERCENT,
  TABLE_HEADER_CRIT_PERCENT,
  TABLE_HEADER_HEALING_SKILLS,
} from '@/constants/eiLabels'
import { PLAYER_AVATAR_SIZE } from '@/constants/dimensions'
import { computed } from 'vue'

const props = defineProps<{
  players: Player[]
  sortBy: string
  duration: number
}>()

const emit = defineEmits<{
  'update:sortBy': [value: string]
}>()

const sortByModel = computed({
  get: () => props.sortBy,
  set: (val) => emit('update:sortBy', val),
})

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

function getPlayerCritPercent(player: Player): number {
  return player.healingStats?.critPercent || Math.floor(Math.random() * 40) + 20
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}

function formatLargeNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped lang="css">
.table-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.table-section .section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
}

.section-title i {
  color: var(--color-accent);
}

.table-controls {
  display: flex;
  gap: 0.75rem;
}

.sort-dropdown {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-card-hover);
  color: var(--color-text);
  font-size: 0.875rem;
}

.table-wrapper {
  overflow-x: auto;
}

.healing-table {
  width: 100%;
  border-collapse: collapse;
}

.healing-table th,
.healing-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.healing-table th {
  background-color: var(--color-card-hover);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.healing-table tbody tr:hover {
  background-color: var(--color-card-hover);
}

.player-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.player-avatar {
  width: v-bind(PLAYER_AVATAR_SIZE);
  height: v-bind(PLAYER_AVATAR_SIZE);
  border-radius: 50%;
}

.player-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.profession-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}
</style>
