<template>
  <div class="player-stats-table bg-neutral-card rounded-[var(--radius-lg)] p-[var(--spacing-lg)] shadow-[var(--shadow-card)]">
    <div class="table-header flex flex-col items-start gap-[var(--spacing-md)] md:flex-row md:justify-between md:items-center mb-[var(--spacing-lg)]">
      <h3 class="table-title text-[var(--font-size-lg)] font-semibold text-neutral-text flex items-center gap-[var(--spacing-sm)]">
        <i class="pi pi-list" />
        玩家统计
      </h3>
      <div class="table-tools flex gap-[var(--spacing-md)]">
        <div class="sort-selector flex items-center gap-[var(--spacing-sm)]">
          <span class="label text-[var(--font-size-sm)] text-neutral-text-secondary">排序:</span>
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

    <div class="table-container overflow-x-auto">
      <table class="w-full border-collapse">
        <thead>
          <tr>
            <th class="rank-col w-12 p-[var(--spacing-md)] text-left text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              #
            </th>
            <th class="player-col min-w-[200px] p-[var(--spacing-md)] text-left text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              玩家
            </th>
            <th class="prof-col w-[100px] p-[var(--spacing-md)] text-left text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              职业
            </th>
            <th class="score-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              评分
            </th>
            <th class="dmg-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              总伤害
            </th>
            <th class="dps-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              DPS
            </th>
            <th class="power-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              直伤
            </th>
            <th class="condi-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              症状
            </th>
            <th class="cc-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              CC
            </th>
            <th class="down-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              倒地
            </th>
            <th class="death-col text-right p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border">
              死亡
            </th>
            <th class="actions-col w-12 text-center p-[var(--spacing-md)] text-[var(--font-size-xs)] font-semibold text-neutral-text-secondary uppercase tracking-wide border-b-2 border-neutral-border" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(player, index) in sortedPlayers"
            :key="player.instanceID"
            class="player-row border-b border-neutral-border-light transition-colors duration-200 hover:bg-[var(--color-hover)]"
            :class="{
              'bg-[var(--color-selected)]': selectedId === player.instanceID,
              'bg-[rgba(255,193,7,0.1)]': player.hasCommanderTag
            }"
            @click="$emit('select-player', player.instanceID)"
          >
            <td class="rank-col w-12 p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span
                class="rank-badge inline-flex items-center justify-center w-7 h-7 rounded-full font-semibold text-[var(--font-size-xs)] bg-neutral-border text-neutral-text-secondary"
                :class="getRankClass(index)"
              >
                {{ index + 1 }}
              </span>
            </td>
            <td class="player-col min-w-[200px] p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <div class="player-info flex items-center gap-[var(--spacing-md)]">
                <img
                  :src="getIconUrl(player.profession)"
                  :alt="player.profession"
                  class="prof-icon w-8 h-8 rounded-full object-cover bg-neutral-border"
                  @error="handleIconError($event)"
                >
                <div class="player-name-group flex flex-col">
                  <span class="player-name font-medium text-neutral-text flex items-center gap-[var(--spacing-xs)]">
                    {{ player.name }}
                    <span
                      v-if="player.hasCommanderTag"
                      class="commander-tag text-[#ffc107]"
                    >
                      <i class="pi pi-star-fill" />
                    </span>
                  </span>
                  <span class="account-name text-[var(--font-size-xs)] text-neutral-text-secondary">{{ player.account }}</span>
                </div>
              </div>
            </td>
            <td class="prof-col w-[100px] p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span 
                class="prof-name inline-block py-1 px-3 rounded-[var(--radius-md)] text-[var(--font-size-xs)] font-medium text-white [text-shadow:0_1px_2px_rgba(0,0,0,0.2)]"
                :style="{ backgroundColor: getColor(player.profession) }"
              >
                {{ getName(player.profession) }}
              </span>
            </td>
            <td class="score-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="score-value font-semibold text-primary">{{ player.total_score }}</span>
            </td>
            <td class="dmg-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="damage-value font-medium text-neutral-text">{{ formatDamage(getPlayerDamage(player)) }}</span>
            </td>
            <td class="dps-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="dps-value font-medium text-neutral-text">{{ player.dps }}</span>
            </td>
            <td class="power-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="power-value font-medium text-neutral-text">{{ formatDamage(getPlayerPowerDamage(player)) }}</span>
            </td>
            <td class="condi-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="condi-value font-medium text-neutral-text">{{ formatDamage(getPlayerCondiDamage(player)) }}</span>
            </td>
            <td class="cc-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="cc-value text-neutral-text-secondary">{{ player.cc || 0 }}</span>
            </td>
            <td class="down-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="down-value text-neutral-text-secondary">{{ player.downs || 0 }}</span>
            </td>
            <td class="death-col text-right p-[var(--spacing-md)] text-[var(--font-size-sm)]">
              <span class="death-value text-neutral-text-secondary">{{ player.deaths || 0 }}</span>
            </td>
            <td class="actions-col w-12 text-center p-[var(--spacing-md)] text-[var(--font-size-sm)]">
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
import { ref, computed, onMounted } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { formatDamage } from '@/types/eliteInsights'
import { useProfession } from '@/composables/useProfession'
import type { Player } from '@/types/eliteInsights'
import { Colors } from '@/config/designTokens'

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

function getRankClass(index: number): string {
  if (index === 0) return 'bg-[#ffc107] text-[#1a1a2e]'
  if (index === 1) return 'bg-[#9e9e9e] text-[#1a1a2e]'
  if (index === 2) return 'bg-[#795548] text-white'
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
  if (!key) return ''
  
  // 先尝试查找基础职业
  const profession = professions.find(p => p.profession_key === key)
  if (profession) return profession.profession_name
  
  // 再尝试查找精英特长
  const spec = eliteSpecs.find(s => s.spec_key === key)
  if (spec) return spec.spec_name
  
  return key
}

function getColor(key: string): string {
  if (!key) return Colors.palette.gray
  
  const profession = professions.find(p => p.profession_key === key)
  if (profession && profession.color) return profession.color
  
  const spec = eliteSpecs.find(s => s.spec_key === key)
  if (spec && spec.color) return spec.color
  
  return Colors.palette.gray
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




