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
                  :src="getIconUrl(player.profession)"
                  :alt="player.profession"
                  class="prof-icon"
                  @error="handleIconError($event)"
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
                class="prof-name"
                :style="{ backgroundColor: getColor(player.profession) }"
              >
                {{ getName(player.profession) }}
              </span>
            </td>
            <td class="score-col">
              <span class="score-value">{{ player.total_score }}</span>
            </td>
            <td class="dmg-col">
              <span class="damage-value">{{ formatDamage(getPlayerDamage(player)) }}</span>
            </td>
            <td class="dps-col">
              <span class="dps-value">{{ player.dps }}</span>
            </td>
            <td class="power-col">
              <span class="power-value">{{ formatDamage(getPlayerPowerDamage(player)) }}</span>
            </td>
            <td class="condi-col">
              <span class="condi-value">{{ formatDamage(getPlayerCondiDamage(player)) }}</span>
            </td>
            <td class="cc-col">
              <span class="cc-value">{{ player.cc || 0 }}</span>
            </td>
            <td class="down-col">
              <span class="down-value">{{ player.downs || 0 }}</span>
            </td>
            <td class="death-col">
              <span class="death-value">{{ player.deaths || 0 }}</span>
            </td>
            <td class="actions-col">
              <BaseButton
                size="small"
                icon="pi pi-eye"
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
import { PLAYER_STATS_SORT_OPTIONS } from '@/constants/dictValues'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { useProfession } from '@/composables/useProfession'
import { getProfessionName } from '@/services/professionService'
import type { Player } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'
import { computed, onMounted, ref } from 'vue'

interface Props {
  players: Player[]
  selectedId: number | null
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'select-player', instanceId: number): void
}>()

// 使用响应式职业数据
const { professions, eliteSpecs, isLoaded, loadProfessionData } = useProfession()

// =============================================
// 状态
// =============================================

type SortKey = 'dps' | 'score' | 'dmg' | 'name'

const currentSort = ref<SortKey>('dps')

const sortOptions = PLAYER_STATS_SORT_OPTIONS.map(o => ({ key: o.key as SortKey, label: o.label }))

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

function getRankClass(index: number): string {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

function handleIconError(event: Event): void {
  const target = event.target as HTMLImageElement
  target.src = ''
}

// =============================================
// 职业数据获取方法（使用响应式数据）
// =============================================

function getName(key: string): string {
  return getProfessionName(key)
}

function getColor(key: string): string {
  if (!key) return '#6b7280'
  
  const profession = professions.find(p => p.profession_key === key)
  if (profession && profession.color) return profession.color
  
  const spec = eliteSpecs.find(s => s.spec_key === key)
  if (spec && spec.color) return spec.color
  
  return '#6b7280'
}

function getIconUrl(key: string): string {
  if (!key) return ''
  
  const profession = professions.find(p => p.profession_key === key)
  if (profession && profession.icon) {
    try {
      return new URL(`/src/assets/images/prof/${profession.icon}`, import.meta.url).href
    } catch (error) {
      console.error(`[PlayerStatsTable] 加载职业图标失败: ${key}`, error)
    }
  }
  
  const spec = eliteSpecs.find(s => s.spec_key === key)
  if (spec && spec.icon) {
    try {
      return new URL(`/src/assets/images/prof/${spec.icon}`, import.meta.url).href
    } catch (error) {
      console.error(`[PlayerStatsTable] 加载精英特长图标失败: ${key}`, error)
    }
  }
  
  return ''
}

// =============================================
// 生命周期
// =============================================

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

.sort-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.sort-selector .label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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

tbody tr {
  border-bottom: 1px solid var(--color-border-light);
  transition: background-color 0.2s ease;
}

tbody tr:hover {
  background-color: var(--color-hover);
}

tbody tr.selected {
  background-color: var(--color-selected);
}

tbody tr.commander {
  background-color: rgba(255, 193, 7, 0.1);
}

tbody td {
  padding: var(--spacing-md);
  font-size: var(--font-size-sm);
}

.rank-col {
  width: 48px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: 600;
  font-size: var(--font-size-xs);
  background-color: var(--color-border);
  color: var(--color-text-secondary);
}

.rank-badge.gold {
  background-color: #ffc107;
  color: #1a1a2e;
}

.rank-badge.silver {
  background-color: #9e9e9e;
  color: #1a1a2e;
}

.rank-badge.bronze {
  background-color: #795548;
  color: #fff;
}

.player-col {
  min-width: 200px;
}

.player-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.prof-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  background-color: var(--color-border);
}

.player-name-group {
  display: flex;
  flex-direction: column;
}

.player-name {
  font-weight: 500;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.commander-tag {
  color: #ffc107;
}

.account-name {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.prof-col {
  width: 100px;
}

.prof-name {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.score-col,
.dps-col,
.dmg-col,
.power-col,
.condi-col,
.cc-col,
.down-col,
.death-col {
  text-align: right;
}

.score-value {
  font-weight: 600;
  color: var(--color-primary);
}

.damage-value,
.dps-value,
.power-value,
.condi-value {
  font-weight: 500;
  color: var(--color-text-primary);
}

.cc-value,
.down-value,
.death-value {
  color: var(--color-text-secondary);
}

.actions-col {
  width: 48px;
  text-align: center;
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .table-tools {
    flex-wrap: wrap;
  }
}

</style>
