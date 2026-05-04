<template>
  <div class="event-timeline-view space-y-6">
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-clock text-primary mr-2" />
        战斗时间线
      </h3>
      <div class="space-y-2">
        <div
          v-for="(event, idx) in timelineEvents"
          :key="idx"
          class="flex items-center gap-4 p-3 rounded-lg hover:bg-neutral-bg/50 transition-colors"
        >
          <div class="w-16 text-xs text-neutral-text-secondary font-mono">
            {{ formatTime(event.time_ms) }}
          </div>
          <div class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="getEventIconClass(event.event_type)"
          >
            <i :class="getEventIcon(event.event_type)" />
          </div>
          <div class="flex-1">
            <span class="font-medium text-neutral-text">{{ getEventLabel(event.event_type) }}</span>
            <span v-if="event.agent_name" class="text-sm text-neutral-text-secondary ml-2">
              — {{ event.agent_name }}
            </span>
          </div>
        </div>
        <div v-if="timelineEvents.length === 0" class="text-center py-8 text-neutral-text-secondary">
          <i class="pi pi-inbox text-4xl mb-2" />
          <p>暂无时间线数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  events: any[];
}>();

const timelineEvents = computed(() => {
  return (props.events || []).slice(0, 200);
});

function formatTime(ms: number): string {
  const sec = Math.floor(ms / 1000);
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function getEventIcon(type: string): string {
  const map: Record<string, string> = {
    change_dead: 'pi pi-times-circle',
    change_down: 'pi pi-arrow-down',
    change_up: 'pi pi-arrow-up',
    spawn: 'pi pi-user-plus',
    despawn: 'pi pi-user-minus',
    weapon_swap: 'pi pi-sync',
    enter_combat: 'pi pi-play',
    exit_combat: 'pi pi-pause',
  };
  return map[type] || 'pi pi-circle';
}

function getEventIconClass(type: string): string {
  const map: Record<string, string> = {
    change_dead: 'bg-status-error/20 text-status-error',
    change_down: 'bg-status-warning/20 text-status-warning',
    change_up: 'bg-status-success/20 text-status-success',
    spawn: 'bg-primary/20 text-primary',
    despawn: 'bg-neutral-text-disabled/20 text-neutral-text-disabled',
    weapon_swap: 'bg-secondary/20 text-secondary',
  };
  return map[type] || 'bg-neutral-bg text-neutral-text-secondary';
}

function getEventLabel(type: string): string {
  const map: Record<string, string> = {
    change_dead: '死亡',
    change_down: '倒地',
    change_up: '起身',
    spawn: '进入战斗',
    despawn: '离开战斗',
    weapon_swap: '武器切换',
    enter_combat: '进入战斗',
    exit_combat: '退出战斗',
  };
  return map[type] || type;
}
</script>
