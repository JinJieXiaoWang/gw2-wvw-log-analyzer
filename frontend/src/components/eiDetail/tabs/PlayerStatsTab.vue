<template>
  <div class="tab-content">
    <!-- 主要数据卡片 -->
    <div class="stats-grid">
      <div class="stat-card damage">
        <div class="stat-icon">
          <i class="pi pi-bolt" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ fmtNum(player.dpsAll?.[0]?.damage) }}</span>
          <span class="stat-label">{{ LABEL_TOTAL_DAMAGE }}</span>
        </div>
      </div>
      <div class="stat-card dps">
        <div class="stat-icon">
          <i class="pi pi-gauge" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ player.dps }}</span>
          <span class="stat-label">{{ LABEL_DPS }}</span>
        </div>
      </div>
      <div class="stat-card score">
        <div class="stat-icon">
          <i class="pi pi-trophy" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ player.total_score }}</span>
          <span class="stat-label">{{ LABEL_SCORE }}</span>
        </div>
      </div>
      <div class="stat-card hps">
        <div class="stat-icon">
          <i class="pi pi-heart" />
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ player.hps || 0 }}</span>
          <span class="stat-label">{{ LABEL_HPS }}</span>
        </div>
      </div>
    </div>

    <!-- 详细数据 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-chart-bar" />
        {{ SECTION_BATTLE_DETAILS }}
      </h4>
      <div class="detail-grid">
        <div
          v-for="item in detailItems"
          :key="item.label"
          class="detail-item"
        >
          <span class="detail-label">{{ item.label }}</span>
          <span class="detail-value">{{ item.value }}</span>
        </div>
      </div>
    </div>

    <!-- 战斗状态 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-shield" />
        {{ SECTION_BATTLE_STATUS }}
      </h4>
      <div class="status-grid">
        <div
          v-for="s in statusItems"
          :key="s.label"
          class="status-item"
          :class="{ danger: s.danger }"
        >
          <i :class="s.icon" />
          <div class="status-data">
            <span class="status-value">{{ s.value }}</span>
            <span class="status-label">{{ s.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 武器配置 -->
    <div class="detail-section">
      <h4 class="section-title">
        <i class="pi pi-sword" />
        {{ SECTION_WEAPON_CONFIG }}
      </h4>
      <div class="weapons-box">
        <span class="weapons-text">{{ player.weapons?.join(' / ') || LABEL_WEAPONS_NOT_RECORDED }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player } from '@/types/eliteInsights'
import {
  LABEL_TOTAL_DAMAGE,
  LABEL_DPS,
  LABEL_SCORE,
  LABEL_HPS,
  SECTION_BATTLE_DETAILS,
  LABEL_DIRECT_DAMAGE,
  LABEL_CONDITION_DAMAGE,
  LABEL_CRIT_RATE,
  LABEL_CRIT_DAMAGE,
  LABEL_PRECISION,
  LABEL_POWER,
  LABEL_TOUGHNESS,
  LABEL_VITALITY,
  SECTION_BATTLE_STATUS,
  LABEL_DOWNS,
  LABEL_DEATHS,
  LABEL_CC,
  LABEL_CLEARS,
  SECTION_WEAPON_CONFIG,
  LABEL_WEAPONS_NOT_RECORDED,
} from '@/constants/eiLabels'
import { NUMBER_MILLION, NUMBER_THOUSAND } from '@/constants/thresholds'
import {
  COLOR_DAMAGE_START,
  COLOR_DAMAGE_END,
  COLOR_DPS_START,
  COLOR_DPS_END,
  COLOR_SCORE_START,
  COLOR_SCORE_END,
  COLOR_HEALING_START,
  COLOR_SURVIVAL_END,
} from '@/constants/colors'

const { player } = defineProps<{
  player: Player
}>()

const fmtNum = (n?: number) => {
  const num = n || 0
  if (num >= NUMBER_MILLION) return (num / NUMBER_MILLION).toFixed(1) + 'M'
  if (num >= NUMBER_THOUSAND) return (num / NUMBER_THOUSAND).toFixed(1) + 'K'
  return num.toString()
}

const detailItems = computed(() => [
  { label: LABEL_DIRECT_DAMAGE, value: fmtNum(player.dpsAll?.[0]?.powerDamage) },
  { label: LABEL_CONDITION_DAMAGE, value: fmtNum(player.dpsAll?.[0]?.condiDamage) },
  { label: LABEL_CRIT_RATE, value: (player.critRate || 0) + '%' },
  { label: LABEL_CRIT_DAMAGE, value: (player.critDamage || 0) + '%' },
  { label: LABEL_PRECISION, value: (player.precision || 0).toString() },
  { label: LABEL_POWER, value: (player.power || 0).toString() },
  { label: LABEL_TOUGHNESS, value: (player.toughness || 0).toString() },
  { label: LABEL_VITALITY, value: (player.vitality || 0).toString() },
])

const statusItems = computed(() => [
  { icon: 'pi pi-skull-crossbones', value: player.downs, label: LABEL_DOWNS, danger: player.downs > 0 },
  { icon: 'pi pi-heart-broken', value: player.deaths, label: LABEL_DEATHS, danger: player.deaths > 0 },
  { icon: 'pi pi-shield', value: player.cc, label: LABEL_CC, danger: false },
  { icon: 'pi pi-wind', value: player.cleanses, label: LABEL_CLEARS, danger: false },
])
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}
.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.625rem;
}
.stat-card.damage .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_DAMAGE_START), v-bind(COLOR_DAMAGE_END));
}
.stat-card.dps .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_DPS_START), v-bind(COLOR_DPS_END));
}
.stat-card.score .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_SCORE_START), v-bind(COLOR_SCORE_END));
}
.stat-card.hps .stat-icon {
  background: linear-gradient(135deg, v-bind(COLOR_HEALING_START), v-bind(COLOR_SURVIVAL_END));
}
.stat-icon i {
  font-size: 1.375rem;
  color: white;
}
.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}
.stat-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-text);
}
.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.detail-section {
  margin-bottom: 1.5rem;
}
.detail-section:last-child {
  margin-bottom: 0;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.875rem 0;
}
.section-title i {
  color: var(--color-primary);
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.625rem;
}
.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}
.detail-label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}
.detail-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
}
.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  padding: 0.875rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.625rem;
  border: 1px solid var(--color-border);
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
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}
.status-item.danger .status-value {
  color: var(--color-error);
}
.status-label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.weapons-box {
  padding: 0.875rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.625rem;
  border: 1px solid var(--color-border);
}
.weapons-text {
  font-size: 0.875rem;
  color: var(--color-text);
}
@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
