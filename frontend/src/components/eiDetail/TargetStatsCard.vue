<template>
  <div class="target-stats-card">
    <div class="card-header">
      <div class="header-title">
        <i class="pi pi-crosshair" />
        <span>目标统计</span>
      </div>
    </div>

    <div class="target-list">
      <div
        v-for="target in targets"
        :key="target.instanceID"
        class="target-item"
      >
        <div class="target-header">
          <img
            :src="target.icon"
            class="target-icon"
          >
          <div class="target-info">
            <span class="target-name">{{ target.name }}</span>
            <span class="target-meta">
              <span
                v-if="target.enemyPlayer"
                class="player-tag"
              >敌方玩家</span>
              <span
                v-else
                class="npc-tag"
              >NPC</span>
            </span>
          </div>
          <div
            class="target-status"
            :class="{ dead: target.finalHealth === 0 }"
          >
            <i
              class="pi"
              :class="target.finalHealth === 0 ? 'pi-skull' : 'pi-heart'"
            />
          </div>
        </div>
        <div class="target-stats">
          <div class="stat-item">
            <span class="label">伤害承受</span>
            <span class="value">{{ formatDamage(getTargetDamageTaken(target)) }}</span>
          </div>
          <div class="stat-item">
            <span class="label">存活时间</span>
            <span class="value">{{ formatDuration(target.lastAware - target.firstAware) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Target } from '@/types/eliteInsights'
import { formatDamage, formatDuration } from '@/types/eliteInsights'

interface Props {
  targets: Target[]
}

defineProps<Props>()

function getTargetDamageTaken(target: Target): number {
  return target.statsAll?.[0]?.totalDmg || 0
}
</script>

<style scoped lang="css">
.target-stats-card {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 1.25rem;
}

.card-header {
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

.target-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.target-item {
  padding: 0.875rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.target-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.target-icon {
  width: 40px;
  height: 40px;
  border-radius: 0.5rem;
  background-color: var(--color-card-hover);
}

.target-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.target-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.target-meta {
  font-size: 0.7rem;
}

.player-tag {
  padding: 0.125rem 0.375rem;
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-radius: 9999px;
}

.npc-tag {
  padding: 0.125rem 0.375rem;
  background-color: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border-radius: 9999px;
}

.target-status {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.target-status.dead {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.target-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item .label {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.stat-item .value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>