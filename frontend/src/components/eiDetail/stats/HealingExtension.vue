<template>
  <div class="healing-extension flex flex-col gap-6">
    <!-- 标题 -->
    <div class="section-header mb-4">
      <h2 class="section-title flex items-center gap-2 text-lg font-semibold text-neutral-text m-0 mb-1">
        <i class="pi pi-heart text-[var(--color-accent)]" />
        治疗统计
      </h2>
      <div class="section-subtitle text-sm text-neutral-text-secondary">
        显示团队治疗数据和屏障统计
      </div>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-overview grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-4">
      <div class="stat-card healing flex items-center gap-4 p-5 bg-neutral-card rounded-xl border border-neutral-border">
        <div class="stat-icon w-[52px] h-[52px] flex items-center justify-center rounded-xl bg-[linear-gradient(135deg,#22c55e,#16a34a)]">
          <i class="pi pi-heart text-2xl text-white" />
        </div>
        <div class="stat-info flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">总治疗量</span>
          <span class="stat-value text-2xl font-bold text-neutral-text">{{ formatLargeNumber(totalHealing) }}</span>
        </div>
      </div>
      <div class="stat-card barrier flex items-center gap-4 p-5 bg-neutral-card rounded-xl border border-neutral-border">
        <div class="stat-icon w-[52px] h-[52px] flex items-center justify-center rounded-xl bg-[linear-gradient(135deg,#3b82f6,#1d4ed8)]">
          <i class="pi pi-shield text-2xl text-white" />
        </div>
        <div class="stat-info flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">总屏障量</span>
          <span class="stat-value text-2xl font-bold text-neutral-text">{{ formatLargeNumber(totalBarrier) }}</span>
        </div>
      </div>
      <div class="stat-card hps flex items-center gap-4 p-5 bg-neutral-card rounded-xl border border-neutral-border">
        <div class="stat-icon w-[52px] h-[52px] flex items-center justify-center rounded-xl bg-[linear-gradient(135deg,#8b5cf6,#6d28d9)]">
          <i class="pi pi-gauge text-2xl text-white" />
        </div>
        <div class="stat-info flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">平均HPS</span>
          <span class="stat-value text-2xl font-bold text-neutral-text">{{ formatLargeNumber(avgHps) }}</span>
        </div>
      </div>
      <div class="stat-card overheal flex items-center gap-4 p-5 bg-neutral-card rounded-xl border border-neutral-border">
        <div class="stat-icon w-[52px] h-[52px] flex items-center justify-center rounded-xl bg-[linear-gradient(135deg,#f59e0b,#d97706)]">
          <i class="pi pi-chart-pie text-2xl text-white" />
        </div>
        <div class="stat-info flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">过量治疗</span>
          <span class="stat-value text-2xl font-bold text-neutral-text">{{ overhealPercent }}%</span>
        </div>
      </div>
    </div>

    <!-- 治疗/屏障分布图表 -->
    <div class="chart-section bg-neutral-card rounded-xl border border-neutral-border p-5">
      <div class="chart-header flex items-center justify-between mb-5">
        <h3 class="chart-title text-base font-semibold text-neutral-text m-0">
          治疗与屏障分布
        </h3>
        <div class="chart-tabs flex gap-2">
          <button
            v-for="tab in distributionTabs"
            :key="tab.key"
            class="chart-tab py-2 px-3 border-none rounded-lg text-[0.8125rem] cursor-pointer transition-all duration-200"
            :class="[
              activeDistributionTab === tab.key
                ? 'bg-[var(--color-accent)] text-white'
                : 'bg-neutral-card-hover text-neutral-text-secondary hover:bg-neutral-border'
            ]"
            @click="activeDistributionTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
      <div class="chart-container">
        <div class="bar-chart flex flex-col gap-3">
          <div
            v-for="(player, index) in sortedHealers.slice(0, 10)"
            :key="player.instanceID"
            class="bar-item flex items-center gap-3"
          >
            <div class="bar-rank w-7 h-7 flex items-center justify-center bg-neutral-card-hover rounded-full text-xs font-semibold text-neutral-text-secondary">
              {{ index + 1 }}
            </div>
            <div class="bar-info w-[150px] flex flex-col">
              <span class="bar-name text-sm font-medium text-neutral-text">{{ player.name }}</span>
              <span class="bar-profession text-xs text-neutral-text-secondary">{{ getProfessionName(player.profession) }}</span>
            </div>
            <div class="bar-wrapper flex-1 h-5 bg-neutral-card-hover rounded-sm relative overflow-hidden">
              <div
                class="bar-fill absolute top-0 h-full transition-[width] duration-300 left-0 bg-[linear-gradient(90deg,#22c55e,#16a34a)] rounded-l-sm"
                :style="{ width: getHealingPercent(player) + '%' }"
              />
              <div
                class="bar-fill absolute top-0 h-full transition-[width] duration-300 bg-[linear-gradient(90deg,#3b82f6,#1d4ed8)] rounded-r-sm"
                :style="{
                  width: getBarrierPercent(player) + '%',
                  left: getHealingPercent(player) + '%'
                }"
              />
            </div>
            <div class="bar-value w-[100px] text-right text-sm font-semibold text-neutral-text">
              {{ formatLargeNumber(getPlayerHealing(player) + getPlayerBarrier(player)) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 治疗技能统计 -->
    <div class="skill-section bg-neutral-card rounded-xl border border-neutral-border p-5">
      <div class="section-header mb-4">
        <h3 class="section-title flex items-center gap-2 text-lg font-semibold text-neutral-text m-0 mb-1">
          <i class="pi pi-sword text-[var(--color-accent)]" />
          治疗技能统计
        </h3>
      </div>
      <div class="skill-grid grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
        <div
          v-for="skill in healingSkills"
          :key="skill.id"
          class="skill-card bg-neutral-card-hover rounded-lg p-4"
        >
          <div class="skill-header flex justify-between items-center mb-3">
            <span class="skill-name text-sm font-semibold text-neutral-text">{{ skill.name }}</span>
            <span class="skill-count text-xs text-green-500 font-medium">{{ skill.count }} 次</span>
          </div>
          <div class="skill-stats flex gap-4">
            <div class="skill-stat flex flex-col gap-0.5">
              <span class="stat-label text-[0.7rem] text-[var(--color-text-tertiary)]">治疗量</span>
              <span class="stat-value text-sm font-semibold text-neutral-text">{{ formatLargeNumber(skill.healing) }}</span>
            </div>
            <div class="skill-stat flex flex-col gap-0.5">
              <span class="stat-label text-[0.7rem] text-[var(--color-text-tertiary)]">过量%</span>
              <span class="stat-value text-sm font-semibold text-neutral-text">{{ skill.overhealPercent }}%</span>
            </div>
            <div class="skill-stat flex flex-col gap-0.5">
              <span class="stat-label text-[0.7rem] text-[var(--color-text-tertiary)]">目标数</span>
              <span class="stat-value text-sm font-semibold text-neutral-text">{{ skill.targets }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 玩家治疗详情表格 -->
    <div class="table-section bg-neutral-card rounded-xl border border-neutral-border overflow-hidden">
      <div class="section-header flex items-center justify-between p-4 px-5 bg-neutral-card-hover border-b border-neutral-border mb-0">
        <h3 class="section-title flex items-center gap-2 text-lg font-semibold text-neutral-text m-0 mb-1">
          <i class="pi pi-users text-[var(--color-accent)]" />
          玩家治疗详情
        </h3>
        <div class="table-controls flex gap-3">
          <select
            v-model="sortBy"
            class="sort-dropdown py-2 px-3 border border-neutral-border rounded-lg bg-neutral-card-hover text-neutral-text text-sm"
          >
            <option value="healing">
              治疗量
            </option>
            <option value="barrier">
              屏障量
            </option>
            <option value="hps">
              HPS
            </option>
            <option value="overheal">
              过量治疗
            </option>
          </select>
        </div>
      </div>
      <div class="table-wrapper overflow-x-auto">
        <table class="healing-table w-full border-collapse">
          <thead>
            <tr>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">#</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">玩家</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">职业</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">治疗量</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">屏障量</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">HPS</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">过量%</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">暴击%</th>
              <th class="py-3 px-4 text-left border-b border-neutral-border bg-neutral-card-hover text-xs font-semibold text-neutral-text-secondary uppercase tracking-wider">治疗技能</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(player, index) in sortedHealers"
              :key="player.instanceID"
              class="hover:bg-neutral-card-hover transition-colors duration-200"
            >
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ index + 1 }}</td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">
                <div class="player-cell flex items-center gap-2">
                  <img
                    :src="getProfIcon(player.profession)"
                    class="player-avatar w-7 h-7 rounded-full"
                  >
                  <span class="player-name text-sm font-medium text-neutral-text">{{ player.name }}</span>
                </div>
              </td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">
                <span
                  class="profession-badge py-1 px-2 rounded text-xs font-medium text-white"
                  :style="{ backgroundColor: getProfessionColor(player.profession) }"
                >
                  {{ getProfessionName(player.profession) }}
                </span>
              </td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ formatLargeNumber(getPlayerHealing(player)) }}</td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ formatLargeNumber(getPlayerBarrier(player)) }}</td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ formatLargeNumber(getPlayerHps(player)) }}</td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ getPlayerOverhealPercent(player) }}%</td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ getPlayerCritPercent(player) }}%</td>
              <td class="py-3 px-4 text-left border-b border-neutral-border text-sm">{{ player.healingSkillsCount || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'

const props = defineProps<{
  players: Player[]
  duration: number
}>()

const sortBy = ref('healing')
const activeDistributionTab = ref('combined')

const distributionTabs = [
  { key: 'healing', label: '仅治疗' },
  { key: 'barrier', label: '仅屏障' },
  { key: 'combined', label: '综合' }
]

// 模拟治疗技能数据
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

// 计算属性
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

// 方法
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

function getHealingPercent(player: Player): number {
  const max = Math.max(...props.players.map(p => getPlayerHealing(p)), 1)
  return (getPlayerHealing(player) / max) * 100
}

function getBarrierPercent(player: Player): number {
  const max = Math.max(...props.players.map(p => getPlayerBarrier(p)), 1)
  return (getPlayerBarrier(player) / max) * 100
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
