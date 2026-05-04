<template>
  <div class="squad-overview">
    <div class="overview-grid">
      <!-- 伤害统计 -->
      <div class="stat-card damage">
        <div class="stat-header">
          <div class="stat-icon">
            <i class="pi pi-bolt" />
          </div>
          <span class="stat-label">总伤害</span>
        </div>
        <div class="stat-value">
          {{ formatNumber(damage.total) }}
        </div>
        <div class="stat-detail">
          <span class="detail-item power">直伤 {{ formatNumber(damage.power) }}</span>
          <span class="detail-divider">|</span>
          <span class="detail-item condi">症状 {{ formatNumber(damage.condi) }}</span>
        </div>
        <div class="stat-footer">
          <span class="avg-dps">小队平均 DPS: {{ formatNumber(damage.avgDps) }}</span>
        </div>
      </div>

      <!-- 防御统计 -->
      <div class="stat-card defense">
        <div class="stat-header">
          <div class="stat-icon">
            <i class="pi pi-shield" />
          </div>
          <span class="stat-label">防御</span>
        </div>
        <div class="stat-row">
          <div class="stat-sub">
            <span class="sub-value">{{ defenses.totalDown }}</span>
            <span class="sub-label">倒地</span>
          </div>
          <div class="stat-sub">
            <span
              class="sub-value"
              :class="{ danger: defenses.totalDead > 0 }"
            >{{ defenses.totalDead }}</span>
            <span class="sub-label">死亡</span>
          </div>
          <div class="stat-sub">
            <span class="sub-value">{{ formatNumber(defenses.totalDamageTaken) }}</span>
            <span class="sub-label">承伤</span>
          </div>
        </div>
      </div>

      <!-- 支援统计 -->
      <div class="stat-card support">
        <div class="stat-header">
          <div class="stat-icon">
            <i class="pi pi-heart" />
          </div>
          <span class="stat-label">支援</span>
        </div>
        <div class="stat-row">
          <div class="stat-sub">
            <span class="sub-value">{{ formatNumber(support.totalCleanse) }}</span>
            <span class="sub-label">清症</span>
          </div>
          <div class="stat-sub">
            <span class="sub-value">{{ formatNumber(support.totalHealing) }}</span>
            <span class="sub-label">治疗</span>
          </div>
        </div>
      </div>

      <!-- 小队构成 -->
      <div class="stat-card composition">
        <div class="stat-header">
          <div class="stat-icon">
            <i class="pi pi-sitemap" />
          </div>
          <span class="stat-label">小队构成</span>
        </div>
        <div class="composition-list">
          <div
            v-for="prof in topProfessions"
            :key="prof.name"
            class="comp-item"
          >
            <span
              class="comp-dot"
              :style="{ backgroundColor: getProfessionColor(prof.name) }"
            />
            <span class="comp-name">{{ prof.name }}</span>
            <span class="comp-count">×{{ prof.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getProfessionColor } from '@/utils/profession/professionUtils'

interface Props {
  damage: {
    total: number
    power: number
    condi: number
    avgDps: number
  }
  defenses: {
    totalDown: number
    totalDead: number
    totalDamageTaken: number
  }
  support: {
    totalCleanse: number
    totalHealing: number
  }
  professions: Array<{ name: string; count: number; damage: number }>
}

const props = defineProps<Props>()

const topProfessions = computed(() => props.professions.slice(0, 5))

function formatNumber(n: number | undefined | null): string {
  if (n === undefined || n === null || isNaN(n)) return '-'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}
</script>

<style scoped>
.squad-overview {
  padding: 0 1.5rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.stat-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.damage .stat-icon {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.defense .stat-icon {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.support .stat-icon {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.composition .stat-icon {
  background: rgba(168, 85, 247, 0.15);
  color: #a855f7;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.stat-detail {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  margin-bottom: 0.5rem;
}

.detail-item.power {
  color: #f59e0b;
}

.detail-item.condi {
  color: #a855f7;
}

.detail-divider {
  color: var(--text-color-secondary);
  opacity: 0.5;
}

.stat-footer {
  font-size: 0.8125rem;
  color: var(--text-color-secondary);
}

.stat-row {
  display: flex;
  gap: 1.5rem;
}

.stat-sub {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.sub-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.2;
}

.sub-value.danger {
  color: #ef4444;
}

.sub-label {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  margin-top: 0.125rem;
}

.composition-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.comp-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  background: var(--surface-hover);
  border-radius: 0.375rem;
}

.comp-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.comp-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
  flex: 1;
}

.comp-count {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-color-secondary);
}
</style>
