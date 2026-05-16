<template>
  <div class="event-log">
    <h3 class="log-title">
      <i class="pi pi-list" /> 战斗事件
    </h3>
    <div class="log-content">
      <div
        v-for="event in recentEvents"
        :key="event.id"
        class="log-item"
        :class="event.type"
      >
        <span class="log-time">{{ formatTime(event.time) }}</span>
        <span class="log-content-text">{{ event.content }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  events: any[]
  currentTime: number
}>()

const recentEvents = computed(() => props.events.filter((e: any) => e.time <= props.currentTime).slice(-20))

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped lang="css">
.event-log {
  background-color: var(--color-card);
  border-radius: 0.75rem;
  padding: 1rem;
  max-height: 200px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.75rem 0;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.log-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem;
  background-color: var(--color-card-hover);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
}

.log-time {
  font-family: monospace;
  color: var(--color-accent);
  font-weight: 500;
}

.log-content-text {
  color: var(--color-text-secondary);
}

.log-item.damage {
  border-left: 3px solid #ef4444;
}

.log-item.heal {
  border-left: 3px solid #22c55e;
}

.log-item.buff {
  border-left: 3px solid #f59e0b;
}

.log-item.cc {
  border-left: 3px solid #8b5cf6;
}
</style>
