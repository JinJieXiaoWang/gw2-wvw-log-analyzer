<template>
  <div class="boons-uptime-card">
    <div class="card-header">
      <div class="header-title">
        <i class="pi pi-shield" />
        <span>增益覆盖</span>
      </div>
    </div>

    <div class="boons-container">
      <div
        v-for="boon in topBoons"
        :key="boon.id"
        class="boon-item"
      >
        <div class="boon-header">
          <span class="boon-name">{{ boon.name }}</span>
          <span
            class="boon-uptime"
            :class="getUptimeClass(boon.uptime)"
          >
            {{ boon.uptime }}%
          </span>
        </div>
        <div class="boon-bar-container">
          <div
            class="boon-bar-fill"
            :style="{ width: boon.uptime + '%', backgroundColor: boon.color }"
          />
        </div>
        <div class="boon-stats">
          <span class="stat">应用: {{ boon.applied }}</span>
          <span class="stat">浪费: {{ boon.wasted }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface BoonData {
  id: number
  name: string
  uptime: number
  applied: number
  wasted: number
  color: string
}

interface Props {
  boonsData: BoonData[]
}

const props = defineProps<Props>()

const topBoons = computed(() => {
  return [...props.boonsData].sort((a, b) => b.uptime - a.uptime).slice(0, 6)
})

function getUptimeClass(uptime: number): string {
  if (uptime >= 80) return 'high'
  if (uptime >= 50) return 'medium'
  return 'low'
}
</script>

<style scoped lang="css">
.boons-uptime-card {
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

.boons-container {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.boon-item {
  padding: 0.75rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.boon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.boon-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.boon-uptime {
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  background-color: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.boon-uptime.high {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.boon-uptime.medium {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.boon-uptime.low {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.boon-bar-container {
  height: 6px;
  background-color: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.boon-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.boon-stats {
  display: flex;
  gap: 1rem;
}

.stat {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
}
</style>