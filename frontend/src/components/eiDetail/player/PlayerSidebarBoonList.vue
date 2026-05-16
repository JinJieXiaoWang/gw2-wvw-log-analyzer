<template>
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
</template>

<script setup lang="ts">
import type { Player } from '@/types/eliteInsights';

interface Props {
  player: Player
}

defineProps<Props>()
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

.boon-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  max-height: 150px;
  overflow-y: auto;
}

.boon-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: var(--color-bg);
  border-radius: 0.375rem;
  font-size: 0.75rem;
}

.boon-id {
  color: var(--color-text-secondary);
}

.boon-value {
  color: var(--color-text);
  font-weight: 500;
}

.empty-boons {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-disabled);
  padding: 1rem;
}
</style>
