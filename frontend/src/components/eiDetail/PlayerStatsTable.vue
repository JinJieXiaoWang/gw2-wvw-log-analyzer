<template>
  <div class="player-stats-table">
    <div class="table-header">
      <h3 class="table-title">
        <i class="pi pi-list" />
        玩家统计
      </h3>
      <div class="table-tools">
        <div class="sort-selector">
          <span class="label">排序:</span>
          <Button
            v-for="sort in sortOptions"
            :key="sort.key"
            size="small"
            :outlined="currentSort !== sort.key"
            :label="sort.label"
            @click="setSort(sort.key)"
          />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th class="rank-col">
              #
            </th>
            <th class="player-col">
              玩家
            </th>
            <th class="prof-col">
              职业
            </th>
            <th class="score-col">
              评分
            </th>
            <th class="dmg-col">
              总伤害
            </th>
            <th class="dps-col">
              DPS
            </th>
            <th class="power-col">
              直伤
            </th>
            <th class="condi-col">
              症状
            </th>
            <th class="cc-col">
              CC
            </th>
            <th class="down-col">
              倒地
            </th>
            <th class="death-col">
              死亡
            </th>
            <th class="actions-col" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(player, index) in sortedPlayers"
            :key="player.instanceID"
            class="player-row"
            :class="{
              selected: selectedId === player.instanceID,
              commander: player.hasCommanderTag
            }"
            @click="$emit('select-player', player.instanceID)"
          >
            <td class="rank-col">
              <span
                class="rank-badge"
                :class="getRankClass(index)"
              >
                {{ index + 1 }}
              </span>
            </td>
            <td class="player-col">
              <div class="player-info">
                <img
                  :src="getProfIcon(player.profession)"
                  :alt="player.profession"
                  class="prof-icon"
                >
                <div class="player-name-group">
                  <span class="player-name">
                    {{ player.name }}
                    <span
                      v-if="player.hasCommanderTag"
                      class="commander-tag"
                    >
                      <i class="pi pi-star-fill" />
                    </span>
                  </span>
                  <span class="account-name">{{ player.account }}</span>
                </div>
              </div>
            </td>
            <td class="prof-col">
              <span
                class="prof-badge"
                :style="getProfStyle(player.profession)"
              >
                {{ getProfName(player.profession) }}
              </span>
            </td>
            <td class="score-col">
              <div class="score-value">
                {{ player.total_score }}
              </div>
            </td>
            <td class="dmg-col">
              <div class="damage-value">
                {{ formatDamage(getPlayerDamage(player)) }}
              </div>
            </td>
            <td class="dps-col">
              <div class="dps-value">
                {{ formatDamage(player.dps) }}
              </div>
            </td>
            <td class="power-col">
              <div class="power-value">
                {{ formatDamage(getPlayerPowerDamage(player)) }}
              </div>
            </td>
            <td class="condi-col">
              <div class="condi-value">
                {{ formatDamage(getPlayerCondiDamage(player)) }}
              </div>
            </td>
            <td class="cc-col">
              <span class="cc-badge">{{ player.cc }}</span>
            </td>
            <td class="down-col">
              <span
                class="down-badge"
                :class="{ danger: player.downs > 0 }"
              >
                {{ player.downs }}
              </span>
            </td>
            <td class="death-col">
              <span
                class="death-badge"
                :class="{ danger: player.deaths > 0 }"
              >
                {{ player.deaths }}
              </span>
            </td>
            <td class="actions-col">
              <Button
                icon="pi pi-arrow-right"
                size="small"
                rounded
                text
                class="detail-btn"
                @click.stop="$emit('select-player', player.instanceID)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 玩家统计表格组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { ref, computed } from 'vue'
import Button from 'primevue/button'
import { formatDamage } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import type { Player } from '@/types/eliteInsights'

interface Props {
  players: Player[]
  selectedId: number | null
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'select-player', instanceId: number): void
}>()

// =============================================
// 状态
// =============================================

type SortKey = 'dps' | 'score' | 'dmg' | 'name'

const currentSort = ref<SortKey>('dps')

const sortOptions = [
  { key: 'dps' as SortKey, label: 'DPS' },
  { key: 'score' as SortKey, label: '评分' },
  { key: 'dmg' as SortKey, label: '伤害' },
  { key: 'name' as SortKey, label: '名称' }
]

// =============================================
// 计算属性
// =============================================

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

// =============================================
// 方法
// =============================================

function setSort(key: SortKey): void {
  currentSort.value = key
}

function getPlayerDamage(player: Player): number {
  return player.dpsAll?.[0]?.damage || 0
}

function getPlayerPowerDamage(player: Player): number {
  return player.dpsAll?.[0]?.powerDamage || 0
}

function getPlayerCondiDamage(player: Player): number {
  return player.dpsAll?.[0]?.condiDamage || 0
}

function getProfName(prof: string): string {
  return getProfessionName(prof)
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}

function getProfStyle(prof: string): { backgroundColor: string } {
  const color = getProfessionColor(prof)
  return { backgroundColor: color }
}

function getRankClass(index: number): string {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}
</script>

<style scoped lang="css">
.player-stats-table {
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
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-card-hover);
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.table-title i {
  color: var(--color-primary);
}

.table-tools {
  display: flex;
  gap: 0.75rem;
}

.sort-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-selector .label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: var(--color-bg);
}

thead th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  text-align: left;
  border-bottom: 2px solid var(--color-border);
}

tbody tr {
  transition: all 0.2s;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
}

tbody tr:hover {
  background-color: var(--color-card-hover);
}

tbody tr.selected {
  background-color: var(--color-primary-alpha-10);
}

tbody tr.commander .player-name {
  color: var(--color-accent);
}

tbody td {
  padding: 0.875rem 1rem;
  font-size: 0.875rem;
}

.rank-col {
  width: 60px;
  text-align: center;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.875rem;
  background-color: var(--color-card-hover);
  color: var(--color-text-secondary);
}

.rank-badge.gold {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.rank-badge.silver {
  background: linear-gradient(135deg, #9ca3af, #d1d5db);
  color: white;
  box-shadow: 0 2px 8px rgba(156, 163, 175, 0.3);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #cd7f32, #d4956a);
  color: white;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.3);
}

.player-col {
  min-width: 200px;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.prof-icon {
  width: 36px;
  height: 36px;
  border-radius: 0.5rem;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.player-name-group {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.player-name {
  font-weight: 600;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.commander-tag {
  color: var(--color-accent);
  font-size: 0.75rem;
}

.account-name {
  font-size: 0.75rem;
  color: var(--color-text-disabled);
}

.prof-col {
  width: 120px;
}

.prof-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.score-col {
  width: 90px;
  text-align: right;
}

.score-value {
  font-weight: 700;
  color: var(--color-primary);
  font-size: 1rem;
}

.dmg-col,
.dps-col,
.power-col,
.condi-col {
  width: 110px;
  text-align: right;
}

.damage-value,
.dps-value,
.power-value,
.condi-value {
  font-weight: 600;
  color: var(--color-text);
}

.power-value {
  color: #ef4444;
}

.condi-value {
  color: #22c55e;
}

.cc-col {
  width: 80px;
  text-align: center;
}

.cc-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-secondary-alpha-10);
  color: var(--color-secondary);
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.down-col,
.death-col {
  width: 80px;
  text-align: center;
}

.down-badge,
.death-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-card-hover);
  color: var(--color-text-secondary);
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.down-badge.danger,
.death-badge.danger {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.actions-col {
  width: 60px;
  text-align: center;
}

.detail-btn {
  color: var(--color-primary);
}
</style>
