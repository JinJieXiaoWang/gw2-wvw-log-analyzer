<template>
  <div class="team-summary-card">
    <div class="card-header">
      <div class="header-title">
        <i class="pi pi-users" />
        <span>团队统计</span>
      </div>
      <div class="header-badge">
        {{ teamStats.playerCount }} 名玩家
      </div>
    </div>

    <div class="stats-grid">
      <!-- 伤害统计 -->
      <div class="stat-card damage">
        <div class="stat-icon">
          <i class="pi pi-chart-line" />
        </div>
        <div class="stat-content">
          <div class="stat-label">
            总伤害
          </div>
          <div class="stat-value">
            {{ formatDamage(totalDamage.total) }}
          </div>
          <div class="stat-breakdown">
            <span class="power">
              <span class="dot" />
              直伤 {{ formatDamage(totalDamage.power) }}
            </span>
            <span class="condi">
              <span class="dot" />
              症状 {{ formatDamage(totalDamage.condi) }}
            </span>
          </div>
        </div>
      </div>

      <!-- DPS 统计 -->
      <div class="stat-card dps">
        <div class="stat-icon">
          <i class="pi pi-fire" />
        </div>
        <div class="stat-content">
          <div class="stat-label">
            平均 DPS
          </div>
          <div class="stat-value">
            {{ formatDamage(Math.round(teamStats.avgDps)) }}
          </div>
          <div class="stat-sub">
            总计 {{ formatDamage(Math.round(teamStats.totalDps)) }}
          </div>
        </div>
      </div>

      <!-- 生存统计 -->
      <div class="stat-card survival">
        <div class="stat-icon">
          <i class="pi pi-shield" />
        </div>
        <div class="stat-content">
          <div class="stat-label">
            生存数据
          </div>
          <div class="stat-values">
            <span class="down">
              <i class="pi pi-exclamation-triangle" />
              {{ teamStats.totalDowns }}
            </span>
            <span class="death">
              <i class="pi pi-times" />
              {{ teamStats.totalDeaths }}
            </span>
          </div>
        </div>
      </div>

      <!-- 辅助统计 -->
      <div class="stat-card support">
        <div class="stat-icon">
          <i class="pi pi-sparkles" />
        </div>
        <div class="stat-content">
          <div class="stat-label">
            辅助数据
          </div>
          <div class="stat-values">
            <span class="cleanse">
              <i class="pi pi-star" />
              {{ teamStats.totalCleanses }}
            </span>
            <span class="strip">
              <i class="pi pi-eye-slash" />
              {{ teamStats.totalStrips }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 伤害占比进度条 -->
    <div class="damage-bar-container">
      <div class="damage-bar">
        <div
          class="damage-segment power"
          :style="{ width: powerPercent }"
        />
        <div
          class="damage-segment condi"
          :style="{ width: condiPercent }"
        />
      </div>
      <div class="damage-labels">
        <span class="label power">
          <span class="dot" />
          直伤 {{ powerPercent }}
        </span>
        <span class="label condi">
          <span class="dot" />
          症状 {{ condiPercent }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 团队统计卡片组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { computed } from 'vue'
import { formatDamage as formatDmg } from '@/types/eliteInsights'

interface Props {
  teamStats: {
    playerCount: number
    totalDps: number
    avgDps: number
    totalDowns: number
    totalDeaths: number
    totalCleanses: number
    totalStrips: number
  }
  totalDamage: {
    total: number
    power: number
    condi: number
  }
}

const props = defineProps<Props>()

function formatDamage(value: number): string {
  return formatDmg(value)
}

const powerPercent = computed(() => {
  if (props.totalDamage.total === 0) return '0%'
  return ((props.totalDamage.power / props.totalDamage.total) * 100).toFixed(1) + '%'
})

const condiPercent = computed(() => {
  if (props.totalDamage.total === 0) return '0%'
  return ((props.totalDamage.condi / props.totalDamage.total) * 100).toFixed(1) + '%'
})
</script>

<style scoped lang="css">
.team-summary-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.header-title i {
  color: var(--color-accent);
}

.header-badge {
  padding: 0.25rem 0.75rem;
  background-color: var(--color-accent-alpha-10);
  color: var(--color-accent);
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.stat-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--color-accent-alpha-30);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--color-shadow);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  flex-shrink: 0;
}

.stat-card.damage .stat-icon {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.stat-card.dps .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #eab308);
}

.stat-card.survival .stat-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.stat-card.support .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.stat-sub {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-breakdown {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
}

.power {
  color: #ef4444;
}

.condi {
  color: #22c55e;
}

.power .dot,
.condi .dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}

.power .dot {
  background-color: #ef4444;
}

.condi .dot {
  background-color: #22c55e;
}

.stat-values {
  display: flex;
  gap: 1rem;
}

.stat-values span {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}

.damage-bar-container {
  margin-top: 0.75rem;
}

.damage-bar {
  height: 8px;
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  background-color: var(--color-border);
}

.damage-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.damage-segment.power {
  background: linear-gradient(90deg, #ef4444, #f97316);
}

.damage-segment.condi {
  background: linear-gradient(90deg, #22c55e, #10b981);
}

.damage-labels {
  display: flex;
  justify-content: flex-end;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.damage-labels .label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.damage-labels .label.power {
  color: #ef4444;
}

.damage-labels .label.condi {
  color: #22c55e;
}
</style>
