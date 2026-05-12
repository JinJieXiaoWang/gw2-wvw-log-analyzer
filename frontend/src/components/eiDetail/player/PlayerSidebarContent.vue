<template>
  <div class="sidebar-content">
    <!-- 基本信息 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-info-circle" /> 基本信息
      </h4>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">职业</span><span class="value">{{ getProfName(player.profession) }}</span>
        </div>
        <div class="info-item">
          <span class="label">分组</span><span class="value">{{ player.group }}</span>
        </div>
        <div class="info-item">
          <span class="label">评分</span><span class="value score">{{ player.total_score }}</span>
        </div>
        <div class="info-item">
          <span class="label">角色</span><span class="value">{{ player.role }}</span>
        </div>
      </div>
    </div>

    <!-- 伤害统计 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-chart-bar" /> 伤害统计
      </h4>
      <div class="damage-stats">
        <div class="damage-item primary">
          <div class="damage-icon">
            <i class="pi pi-bolt" />
          </div><div class="damage-content">
            <div class="damage-label">
              DPS
            </div><div class="damage-value">
              {{ fmt(player.dps) }}
            </div>
          </div>
        </div>
        <div class="damage-item power">
          <div class="damage-icon">
            <i class="pi pi-fire" />
          </div><div class="damage-content">
            <div class="damage-label">
              直伤
            </div><div class="damage-value">
              {{ fmt(getPowerDmg(player)) }}
            </div>
          </div>
        </div>
        <div class="damage-item condi">
          <div class="damage-icon">
            <i class="pi pi-sparkles" />
          </div><div class="damage-content">
            <div class="damage-label">
              症状
            </div><div class="damage-value">
              {{ fmt(getCondiDmg(player)) }}
            </div>
          </div>
        </div>
      </div>
      <div class="total-damage">
        总伤害: <span class="value">{{ fmt(getDmg(player)) }}</span>
      </div>
    </div>

    <!-- 生存统计 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-shield" /> 生存统计
      </h4>
      <div class="survival-stats">
        <div class="survival-item">
          <i class="pi pi-exclamation-triangle" /><span class="label">倒地</span><span class="value">{{ player.downs }}</span>
        </div>
        <div class="survival-item">
          <i class="pi pi-times" /><span class="label">死亡</span><span class="value">{{ player.deaths }}</span>
        </div>
      </div>
    </div>

    <!-- 辅助统计 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-heart" /> 辅助统计
      </h4>
      <div class="support-stats">
        <div class="support-item">
          <i class="pi pi-star" /><span class="label">症状清除</span><span class="value">{{ player.cleanses }}</span>
        </div>
        <div class="support-item">
          <i class="pi pi-eye-slash" /><span class="label">增益剥离</span><span class="value">{{ player.strips }}</span>
        </div>
        <div class="support-item">
          <i class="pi pi-sync" /><span class="label">CC</span><span class="value">{{ player.cc }}</span>
        </div>
      </div>
    </div>

    <!-- 评分详情 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-percentage" /> 评分详情
      </h4>
      <div class="score-details">
        <div class="score-row">
          <span class="label">有效伤害</span><span class="value">{{ player.score_details.effectiveDamage }}</span>
        </div>
        <div class="score-row">
          <span class="label">CC伤害</span><span class="value">{{ player.score_details.breakbarDamage }}</span>
        </div>
        <div class="score-row">
          <span class="label">生存评分</span><span class="value">{{ player.score_details.survival }}</span>
        </div>
      </div>
    </div>

    <!-- 增益覆盖 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-th-large" /> 主要增益覆盖
      </h4>
      <div class="boon-list">
        <div
          v-for="(value, id) in player.buffs"
          :key="id"
          class="boon-item"
        >
          <span class="boon-id">{{ id }}</span><span class="boon-value">{{ value.uptime_ms }}ms</span>
        </div>
        <div
          v-if="!player.buffs || Object.keys(player.buffs).length === 0"
          class="empty-boons"
        >
          暂无增益数据
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights'
import { getProfessionName } from '@/utils/profession/professionUtils'

const { player } = defineProps<{ player: Player }>()

function getProfName(prof: string) { return getProfessionName(prof) }
function getDmg(p: Player) { return p.dpsAll?.[0]?.damage || 0 }
function getPowerDmg(p: Player) { return p.dpsAll?.[0]?.powerDamage || 0 }
function getCondiDmg(p: Player) { return p.dpsAll?.[0]?.condiDamage || 0 }
function fmt(num: number) {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M'
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped>@import './PlayerDetailSidebar.css';</style>
