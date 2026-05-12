<template>
  <div class="player-detail-card">
    <div class="card-header">
      <div class="player-info-header">
        <img
          :src="getProfIcon(player.profession)"
          class="player-avatar-lg"
        >
        <div class="player-main-info">
          <h3 class="player-name-lg">
            {{ player.name }}
          </h3>
          <span
            class="profession-tag"
            :style="{ backgroundColor: getProfessionColor(player.profession) }"
          >
            {{ getProfessionName(player.profession) }}
          </span>
        </div>
      </div>
      <button
        class="close-btn"
        @click="$emit('close')"
      >
        <i class="pi pi-times" />
      </button>
    </div>

    <div class="card-content">
      <!-- 主要数据 -->
      <div class="stats-grid">
        <div class="stat-box damage">
          <div class="stat-icon">
            <i class="pi pi-bolt" />
          </div>
          <div class="stat-data">
            <span class="stat-value">{{ formatLargeNumber(player.dpsAll?.[0]?.damage || 0) }}</span>
            <span class="stat-label">总伤害</span>
          </div>
        </div>
        <div class="stat-box dps">
          <div class="stat-icon">
            <i class="pi pi-gauge" />
          </div>
          <div class="stat-data">
            <span class="stat-value">{{ player.dps }}</span>
            <span class="stat-label">DPS</span>
          </div>
        </div>
        <div class="stat-box score">
          <div class="stat-icon">
            <i class="pi pi-trophy" />
          </div>
          <div class="stat-data">
            <span class="stat-value">{{ player.total_score }}</span>
            <span class="stat-label">评分</span>
          </div>
        </div>
        <div class="stat-box cleanse">
          <div class="stat-icon">
            <i class="pi pi-minus-circle" />
          </div>
          <div class="stat-data">
            <span class="stat-value">{{ player.support?.[0]?.condiCleanse || 0 }}</span>
            <span class="stat-label">清症</span>
          </div>
        </div>
      </div>

      <!-- 详细数据表格 -->
      <div class="detail-section">
        <h4 class="section-title">
          战斗数据详情
        </h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">直伤</span>
            <span class="detail-value">{{ formatLargeNumber(player.dpsAll?.[0]?.powerDamage || 0) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">症状</span>
            <span class="detail-value">{{ formatLargeNumber(player.dpsAll?.[0]?.condiDamage || 0) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">暴击率</span>
            <span class="detail-value">{{ player.critRate || 0 }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">暴击伤害</span>
            <span class="detail-value">{{ player.critDamage || 0 }}%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">精准</span>
            <span class="detail-value">{{ player.precision || 0 }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">威力</span>
            <span class="detail-value">{{ player.power || 0 }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">坚韧</span>
            <span class="detail-value">{{ player.toughness || 0 }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">体力</span>
            <span class="detail-value">{{ player.vitality || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 战斗状态 -->
      <div class="status-section">
        <h4 class="section-title">
          战斗状态
        </h4>
        <div class="status-grid">
          <div
            class="status-item"
            :class="{ danger: player.downs > 0 }"
          >
            <i class="pi pi-skull-crossbones" />
            <div class="status-data">
              <span class="status-value">{{ player.downs }}</span>
              <span class="status-label">倒地</span>
            </div>
          </div>
          <div
            class="status-item"
            :class="{ danger: player.deaths > 0 }"
          >
            <i class="pi pi-heart-broken" />
            <div class="status-data">
              <span class="status-value">{{ player.deaths }}</span>
              <span class="status-label">死亡</span>
            </div>
          </div>
          <div class="status-item">
            <i class="pi pi-shield" />
            <div class="status-data">
              <span class="status-value">{{ player.cc }}</span>
              <span class="status-label">CC</span>
            </div>
          </div>
          <div class="status-item">
            <i class="pi pi-wind" />
            <div class="status-data">
              <span class="status-value">{{ player.cleanses }}</span>
              <span class="status-label">清除</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 武器配置 -->
      <div class="weapons-section">
        <h4 class="section-title">
          武器配置
        </h4>
        <div class="weapons-info">
          <span class="weapons-text">
            {{ player.weapons?.join(' / ') || '未记录' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'

defineProps<{
  player: Player
}>()

defineEmits(['close'])

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

<style scoped lang="css">@import './PlayerStatsDetail.css';</style>
