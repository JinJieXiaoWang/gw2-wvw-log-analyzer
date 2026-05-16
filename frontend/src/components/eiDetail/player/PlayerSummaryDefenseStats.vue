<template>
  <div class="stat-group">
    <h4 class="group-title">
      <i class="pi pi-shield" />
      防御数据
    </h4>
    <div class="stat-items">
      <div class="stat-item">
        <span class="stat-label">承受伤害</span>
        <span class="stat-value">{{ formatDamage(defense.damageTaken) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">格挡</span>
        <span class="stat-value">{{ defense.blockedCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">闪避</span>
        <span class="stat-value">{{ defense.evadedCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">翻滚</span>
        <span class="stat-value">{{ defense.dodgeCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">屏障</span>
        <span class="stat-value">{{ formatDamage(defense.damageBarrier) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PlayerDefense } from '@/types/eliteInsights'
import { formatDamage } from '@/types/eliteInsights'

interface Props {
  defense: PlayerDefense
}

defineProps<Props>()
</script>

<style scoped lang="css">
.stat-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
}

.group-title i {
  color: var(--color-accent);
}

.stat-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
