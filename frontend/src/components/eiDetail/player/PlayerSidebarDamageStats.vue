<template>
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
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights';

interface Props {
  player: Player
}

defineProps<Props>()

function getDmg(p: Player) {
  return p.dpsAll?.[0]?.damage || 0
}

function getPowerDmg(p: Player) {
  return p.dpsAll?.[0]?.powerDamage || 0
}

function getCondiDmg(p: Player) {
  return p.dpsAll?.[0]?.condiDamage || 0
}

function fmt(num: number) {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M'
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped lang="css">
.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.section-title i {
  color: var(--color-primary);
  font-size: 0.875rem;
}

.damage-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.damage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 0.5rem;
  background-color: var(--color-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.damage-item.primary {
  border-color: var(--color-primary-alpha-30);
  background-color: var(--color-primary-alpha-5);
}

.damage-item.power {
  border-color: rgba(239, 68, 68, 0.3);
  background-color: rgba(239, 68, 68, 0.05);
}

.damage-item.condi {
  border-color: rgba(34, 197, 94, 0.3);
  background-color: rgba(34, 197, 94, 0.05);
}

.damage-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.damage-item.power .damage-icon {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.damage-item.condi .damage-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.damage-icon i {
  color: white;
  font-size: 1.25rem;
}

.damage-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.damage-label {
  font-size: 0.7rem;
  color: var(--color-text-disabled);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.damage-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text);
}

.total-damage {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--color-border);
}

.total-damage .value {
  font-weight: 700;
  color: var(--color-text);
  font-size: 0.875rem;
}
</style>
