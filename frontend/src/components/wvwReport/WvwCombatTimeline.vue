<template>
  <div class="combat-timeline">
    <div class="timeline-header">
      <h3 class="timeline-title">
        <i class="pi pi-history" />
        战斗时间线
      </h3>
      <span class="timeline-count">{{ events.length }} 个事件</span>
    </div>

    <div class="timeline-body">
      <div
        v-for="(event, index) in visibleEvents"
        :key="index"
        class="timeline-item"
      >
        <div
          class="timeline-marker"
          :class="event.eventType"
        />
        <div class="timeline-content">
          <div class="timeline-time">
            {{ formatTime(event.timeMs) }}
          </div>
          <div class="timeline-event">
            <span
              class="event-type"
              :class="event.eventType"
            >
              {{ eventTypeLabel(event.eventType) }}
            </span>
            <span class="event-agent">{{ event.agentName }}</span>
          </div>
        </div>
      </div>

      <button
        v-if="events.length > visibleCount"
        class="show-more-btn"
        @click="visibleCount += 20"
      >
        <i class="pi pi-chevron-down" />
        显示更多 ({{ events.length - visibleCount }})
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WvwTimelineEvent } from '@/services/combat/wvwReportService'

interface Props {
  events: WvwTimelineEvent[]
}

const props = defineProps<Props>()

const visibleCount = ref(15)

const visibleEvents = computed(() => props.events.slice(0, visibleCount.value))

const eventTypeLabels: Record<string, string> = {
  enter_combat: '进入战斗',
  exit_combat: '退出战斗',
  change_up: '起身',
  change_down: '倒地',
  despawn: '消失',
  buff_initial: 'Buff初始化',
}

function eventTypeLabel(type: string): string {
  return eventTypeLabels[type] || type
}

function formatTime(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  const subsec = Math.floor((ms % 1000) / 10)
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}.${subsec.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.combat-timeline {
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--surface-border);
}

.timeline-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.timeline-title i {
  color: #3b82f6;
}

.timeline-count {
  font-size: 0.8125rem;
  color: var(--text-color-secondary);
}

.timeline-body {
  padding: 0.75rem 0;
  max-height: 400px;
  overflow-y: auto;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.5rem 1.25rem;
  position: relative;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: calc(1.25rem + 5px);
  top: 20px;
  bottom: -8px;
  width: 2px;
  background: var(--surface-border);
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.timeline-marker.enter_combat {
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
}

.timeline-marker.exit_combat {
  background: #6b7280;
}

.timeline-marker.change_down {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.timeline-marker.change_up {
  background: #3b82f6;
}

.timeline-marker.despawn {
  background: #a855f7;
}

.timeline-marker.buff_initial {
  background: #f59e0b;
}

.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.timeline-time {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color-secondary);
  font-family: monospace;
}

.timeline-event {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.event-type {
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0.0625rem 0.375rem;
  border-radius: 0.25rem;
}

.event-type.enter_combat {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
}

.event-type.exit_combat {
  background: rgba(107, 114, 128, 0.12);
  color: #6b7280;
}

.event-type.change_down {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.event-type.change_up {
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}

.event-type.despawn {
  background: rgba(168, 85, 247, 0.12);
  color: #a855f7;
}

.event-type.buff_initial {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}

.event-agent {
  font-size: 0.8125rem;
  color: var(--text-color);
  font-weight: 500;
}

.show-more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: calc(100% - 2.5rem);
  margin: 0.75rem 1.25rem;
  padding: 0.5rem;
  background: var(--surface-hover);
  border: 1px solid var(--surface-border);
  border-radius: 0.375rem;
  color: var(--text-color-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.show-more-btn:hover {
  background: var(--surface-border);
}
</style>
