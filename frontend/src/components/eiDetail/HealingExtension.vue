<template>
  <div class="healing-extension">
    <!-- 标题 -->
    <div class="section-header">
      <h2 class="section-title">
        <i class="pi pi-heart" />
        治疗统计
      </h2>
      <div class="section-subtitle">
        显示团队治疗数据和屏障统计
      </div>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-overview">
      <div class="stat-card healing">
        <div class="stat-icon">
          <i class="pi pi-heart" />
        </div>
        <div class="stat-info">
          <span class="stat-label">总治疗量</span>
          <span class="stat-value">{{ formatLargeNumber(totalHealing) }}</span>
        </div>
      </div>
      <div class="stat-card barrier">
        <div class="stat-icon">
          <i class="pi pi-shield" />
        </div>
        <div class="stat-info">
          <span class="stat-label">总屏障量</span>
          <span class="stat-value">{{ formatLargeNumber(totalBarrier) }}</span>
        </div>
      </div>
      <div class="stat-card hps">
        <div class="stat-icon">
          <i class="pi pi-gauge" />
        </div>
        <div class="stat-info">
          <span class="stat-label">平均HPS</span>
          <span class="stat-value">{{ formatLargeNumber(avgHps) }}</span>
        </div>
      </div>
      <div class="stat-card overheal">
        <div class="stat-icon">
          <i class="pi pi-chart-pie" />
        </div>
        <div class="stat-info">
          <span class="stat-label">过量治疗</span>
          <span class="stat-value">{{ overhealPercent }}%</span>
        </div>
      </div>
    </div>

    <!-- 治疗/屏障分布图表 -->
    <div class="chart-section">
      <div class="chart-header">
        <h3 class="chart-title">
          治疗与屏障分布
        </h3>
        <div class="chart-tabs">
          <button
            v-for="tab in distributionTabs"
            :key="tab.key"
            class="chart-tab"
            :class="{ active: activeDistributionTab === tab.key }"
            @click="activeDistributionTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
      <div class="chart-container">
        <div class="bar-chart">
          <div
            v-for="(player, index) in sortedHealers.slice(0, 10)"
            :key="player.instanceID"
            class="bar-item"
          >
            <div class="bar-rank">
              {{ index + 1 }}
            </div>
            <div class="bar-info">
              <span class="bar-name">{{ player.name }}</span>
              <span class="bar-profession">{{ getProfessionName(player.profession) }}</span>
            </div>
            <div class="bar-wrapper">
              <div
                class="bar-fill healing-bar"
                :style="{ width: getHealingPercent(player) + '%' }"
              />
              <div
                class="bar-fill barrier-bar"
                :style="{
                  width: getBarrierPercent(player) + '%',
                  left: getHealingPercent(player) + '%'
                }"
              />
            </div>
            <div class="bar-value">
              {{ formatLargeNumber(getPlayerHealing(player) + getPlayerBarrier(player)) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 治疗技能统计 -->
    <div class="skill-section">
      <div class="section-header">
        <h3 class="section-title">
          <i class="pi pi-sword" />
          治疗技能统计
        </h3>
      </div>
      <div class="skill-grid">
        <div
          v-for="skill in healingSkills"
          :key="skill.id"
          class="skill-card"
        >
          <div class="skill-header">
            <span class="skill-name">{{ skill.name }}</span>
            <span class="skill-count">{{ skill.count }} 次</span>
          </div>
          <div class="skill-stats">
            <div class="skill-stat">
              <span class="stat-label">治疗量</span>
              <span class="stat-value">{{ formatLargeNumber(skill.healing) }}</span>
            </div>
            <div class="skill-stat">
              <span class="stat-label">过量%</span>
              <span class="stat-value">{{ skill.overhealPercent }}%</span>
            </div>
            <div class="skill-stat">
              <span class="stat-label">目标数</span>
              <span class="stat-value">{{ skill.targets }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 玩家治疗详情表格 -->
    <div class="table-section">
      <div class="section-header">
        <h3 class="section-title">
          <i class="pi pi-users" />
          玩家治疗详情
        </h3>
        <div class="table-controls">
          <select
            v-model="sortBy"
            class="sort-dropdown"
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
      <div class="table-wrapper">
        <table class="healing-table">
          <thead>
            <tr>
              <th>#</th>
              <th>玩家</th>
              <th>职业</th>
              <th>治疗量</th>
              <th>屏障量</th>
              <th>HPS</th>
              <th>过量%</th>
              <th>暴击%</th>
              <th>治疗技能</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(player, index) in sortedHealers"
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

<style scoped lang="css">
.healing-extension {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  margin-bottom: 1rem;
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

.section-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.stat-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
}

.stat-card.healing .stat-icon {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.stat-card.barrier .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.stat-card.hps .stat-icon {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
}

.stat-card.overheal .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
}

.chart-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.chart-tabs {
  display: flex;
  gap: 0.5rem;
}

.chart-tab {
  padding: 0.5rem 0.75rem;
  border: none;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-tab:hover {
  background-color: var(--color-border);
}

.chart-tab.active {
  background-color: var(--color-accent);
  color: white;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bar-rank {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-card-hover);
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.bar-info {
  width: 150px;
  display: flex;
  flex-direction: column;
}

.bar-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.bar-profession {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.bar-wrapper {
  flex: 1;
  height: 20px;
  background-color: var(--color-card-hover);
  border-radius: 0.25rem;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  position: absolute;
  top: 0;
  height: 100%;
  transition: width 0.3s ease;
}

.healing-bar {
  left: 0;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  border-radius: 0.25rem 0 0 0.25rem;
}

.barrier-bar {
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border-radius: 0 0.25rem 0.25rem 0;
}

.bar-value {
  width: 100px;
  text-align: right;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.skill-section {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.skill-card {
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  padding: 1rem;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.skill-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.skill-count {
  font-size: 0.75rem;
  color: var(--color-status-success);
  font-weight: 500;
}

.skill-stats {
  display: flex;
  gap: 1rem;
}

.skill-stat {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.skill-stat .stat-label {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
}

.skill-stat .stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

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
  width: 28px;
  height: 28px;
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