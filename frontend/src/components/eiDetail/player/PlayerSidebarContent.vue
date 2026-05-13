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
          </div>
          <div class="damage-content">
            <div class="damage-label">
              DPS
            </div>
            <div class="damage-value">
              {{ fmt(player.dps) }}
            </div>
          </div>
        </div>
        <div class="damage-item power">
          <div class="damage-icon">
            <i class="pi pi-fire" />
          </div>
          <div class="damage-content">
            <div class="damage-label">
              直伤
            </div>
            <div class="damage-value">
              {{ fmt(getPowerDmg(player)) }}
            </div>
          </div>
        </div>
        <div class="damage-item condi">
          <div class="damage-icon">
            <i class="pi pi-sparkles" />
          </div>
          <div class="damage-content">
            <div class="damage-label">
              症状
            </div>
            <div class="damage-value">
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
          <i class="pi pi-exclamation-triangle" /><span class="label">倒地</span><span class="value">
            {{ player.downs }}</span>
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
import type { Player } from '@/types/eliteInsights';
import { getProfessionName } from '@/utils/profession/professionUtils';

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

<style scoped lang="css">
.player-detail-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
}

.player-info-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-avatar-lg {
  width: 56px;
  height: 56px;
  border-radius: 50%;
}

.player-main-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.player-name-lg {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.profession-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
  width: fit-content;
}

.close-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: var(--color-border);
}

.card-content {
  padding: 1.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
}

.stat-box.damage .stat-icon {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.stat-box.dps .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
}

.stat-box.score .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #eab308);
}

.stat-box.cleanse .stat-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.stat-icon i {
  font-size: 1.25rem;
  color: white;
}

.stat-data {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}

.stat-label {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
}

.detail-section,
.status-section,
.weapons-section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.25rem;
}

.detail-label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.detail-value {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
}

.status-item i {
  font-size: 1.5rem;
  color: var(--color-text-secondary);
}

.status-item.danger i {
  color: var(--color-error);
}

.status-data {
  text-align: center;
}

.status-value {
  display: block;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
}

.status-item.danger .status-value {
  color: var(--color-error);
}

.status-label {
  display: block;
  font-size: 0.7rem;
  color: var(--color-text-secondary);
}

.weapons-info {
  padding: 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
}

.weapons-text {
  font-size: 0.875rem;
  color: var(--color-text);
}
</style>
