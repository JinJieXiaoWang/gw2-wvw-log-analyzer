<script setup lang="ts">
// 模块功能：技能循环视图组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { RotationEvent } from '@/models/skillRotation';
import { computed } from 'vue';

interface Props {
  events?: RotationEvent[] | null
}

const props = withDefaults(defineProps<Props>(), {
  events: null
})

const safeEvents = computed(() => {
  if (!Array.isArray(props.events)) return []
  return props.events.filter(event => event !== null && event !== undefined)
})

function formatDuration(ms: number | undefined | null): string {
  if (ms === undefined || ms === null || isNaN(ms)) return '0.00s'
  return (ms / 1000).toFixed(2) + 's'
}
</script>

<template>
  <div class="cycle-view bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <h3 class="text-white text-sm mb-3 font-medium">
      技能循环
    </h3>
    <div class="flex flex-wrap gap-2">
      <div
        v-for="(event, index) in safeEvents"
        :key="event.id || index"
        class="skill-item flex items-center gap-2 bg-[#2a2a2e] rounded-md p-2 border border-[#3a3a3e] hover:border-[#165DFF]"
      >
        <img
          v-if="event.skill_icon"
          :src="event.skill_icon"
          class="w-8 h-8 rounded"
          alt=""
        >
        <div
          v-else
          class="w-8 h-8 rounded bg-[#3a3a3e] flex items-center justify-center text-xs"
        >
          {{ event.skill_name?.charAt(0) || '?' }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-white text-xs truncate">
            {{ event.skill_name || '未知技能' }}
          </div>
          <div class="text-[#909399] text-[10px]">
            {{ formatDuration(event.duration) }}
            <span
              v-if="event.state === 'interrupted'"
              class="text-red-500 ml-1"
            >被打断</span>
            <span
              v-if="event.auto_attack"
              class="text-yellow-500 ml-1"
            >平A</span>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="safeEvents.length === 0"
      class="text-[#909399] text-center py-8"
    >
      暂无技能数据
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
