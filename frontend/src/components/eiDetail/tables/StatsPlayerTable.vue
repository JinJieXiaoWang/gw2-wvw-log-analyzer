<template>
  <div class="player-table-section card">
    <div class="table-header">
      <h3 class="table-title">
        <i class="pi pi-users" /> 玩家列表
      </h3>
      <div class="table-controls">
        <div class="sort-select">
          <select
            v-model="sortBy"
            class="sort-dropdown"
          >
            <option value="damage">
              伤害
            </option>
            <option value="dps">
              DPS
            </option>
            <option value="score">
              评分
            </option>
            <option value="name">
              名称
            </option>
          </select>
        </div>
      </div>
    </div>
    <div class="table-wrapper">
      <table class="player-table">
        <thead>
          <tr>
            <th class="col-rank">
              #
            </th>
            <th class="col-player">
              玩家
            </th>
            <th class="col-profession">
              职业
            </th>
            <th class="col-score">
              评分
            </th>
            <th class="col-damage">
              伤害
            </th>
            <th class="col-dps">
              DPS
            </th>
            <th class="col-power">
              直伤
            </th>
            <th class="col-condi">
              症状
            </th>
            <th class="col-cc">
              CC
            </th>
            <th class="col-downs">
              倒地
            </th>
            <th class="col-deaths">
              死亡
            </th>
            <th class="col-cleanses">
              清除
            </th>
            <th class="col-strips">
              剥离
            </th>
            <th class="col-weapons">
              武器
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(player, index) in sortedPlayers"
            :key="player.instanceID"
            class="player-row"
            :class="{ selected: selectedPlayerId === player.instanceID }"
            @click="emit('select-player', player.instanceID)"
          >
            <td class="col-rank">
              <span
                class="rank-badge"
                :class="getRankClass(index)"
              >{{ index + 1 }}</span>
            </td>
            <td class="col-player">
              <div class="player-cell">
                <img
                  :src="getProfIcon(player.profession)"
                  class="player-avatar"
                >
                <div class="player-info">
                  <span class="player-name">{{ player.name }}</span>
                  <span class="player-account">{{ player.account }}</span>
                </div>
                <span
                  v-if="player.hasCommanderTag"
                  class="commander-icon"
                ><i class="pi pi-star-fill" /></span>
              </div>
            </td>
            <td class="col-profession">
              <span
                class="profession-badge"
                :style="{ backgroundColor: getProfessionColor(player.profession) }"
              >{{ getProfessionName(player.profession) }}</span>
            </td>
            <td class="col-score">
              <span class="score-value">{{ player.total_score }}</span>
            </td>
            <td class="col-damage">
              <span class="damage-value">{{ formatLargeNumber(getPlayerDamage(player)) }}</span>
            </td>
            <td class="col-dps">
              <span class="dps-value">{{ formatLargeNumber(player.dps) }}</span>
            </td>
            <td class="col-power">
              <span class="power-value">{{ formatLargeNumber(getPlayerPowerDamage(player)) }}</span>
            </td>
            <td class="col-condi">
              <span class="condi-value">{{ formatLargeNumber(getPlayerCondiDamage(player)) }}</span>
            </td>
            <td class="col-cc">
              <span class="cc-value">{{ player.cc }}</span>
            </td>
            <td class="col-downs">
              <span
                class="downs-value"
                :class="{ danger: player.downs > 0 }"
              >{{ player.downs }}</span>
            </td>
            <td class="col-deaths">
              <span
                class="deaths-value"
                :class="{ danger: player.deaths > 0 }"
              >{{ player.deaths }}</span>
            </td>
            <td class="col-cleanses">
              <span class="cleanses-value">{{ player.cleanses }}</span>
            </td>
            <td class="col-strips">
              <span class="strips-value">{{ player.strips }}</span>
            </td>
            <td class="col-weapons">
              <span class="weapons-value">{{ player.weapons?.join(' / ') || '-' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'

const { players, selectedPlayerId } = defineProps<{
  players: Player[]
  selectedPlayerId: number | null
}>()

const sortBy = defineModel<string>('sortBy', { default: 'damage' })

const emit = defineEmits(['select-player'])

const sortedPlayers = computed(() => {
  const list = [...players]
  const sortValue = sortBy.value
  switch (sortValue) {
    case 'damage': return list.sort((a, b) => getPlayerDamage(b) - getPlayerDamage(a))
    case 'dps': return list.sort((a, b) => b.dps - a.dps)
    case 'score': return list.sort((a, b) => b.total_score - a.total_score)
    case 'name': return list.sort((a, b) => a.name.localeCompare(b.name))
    default: return list
  }
})

function getPlayerDamage(player: Player): number { return player.dpsAll?.[0]?.damage || 0 }
function getPlayerPowerDamage(player: Player): number { return player.dpsAll?.[0]?.powerDamage || 0 }
function getPlayerCondiDamage(player: Player): number { return player.dpsAll?.[0]?.condiDamage || 0 }
function getProfIcon(prof: string): string { return getProfessionIconUrl(prof) || '' }
function getRankClass(index: number): string {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}
function formatLargeNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped>@import '../stats/StatsView.css';</style>
