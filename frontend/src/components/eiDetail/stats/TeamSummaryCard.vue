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

<style scoped lang="css">@import './TeamSummaryCard.css';</style>
