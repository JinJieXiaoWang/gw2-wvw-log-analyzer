<script setup lang="ts">
// 模块功能：技能时间轴视图组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { RotationEvent } from '@/models/skillRotation'
import { computed } from 'vue'

interface Props {
  events?: RotationEvent[] | null
  totalDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  events: null,
  totalDuration: 300000
})

const safeEvents = computed(() => {
  if (!Array.isArray(props.events)) return []
  return props.events.filter(event => 
    event !== null && 
    event !== undefined && 
    event.cast_time !== undefined
  )
})

const safeDuration = computed(() => props.totalDuration || 300000)

function getPosition(castTime: number): number {
  if (safeDuration.value === 0) return 0
  return (castTime / safeDuration.value) * 100
}

function formatTime(ms: number | undefined | null): string {
  if (ms === undefined || ms === null || isNaN(ms)) return '0:00'
  const seconds = ms / 1000
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="timeline-view bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <h3 class="text-white text-sm mb-3 font-medium">
      时间轴
    </h3>
    <div class="timeline-container relative h-24 bg-[#2a2a2e] rounded-md overflow-hidden">
      <!-- 时间标记 -->
      <div class="absolute inset-x-0 top-0 flex justify-between px-2 text-[10px] text-[#909399]">
        <span>0:00</span>
        <span>1:00</span>
        <span>2:00</span>
        <span>3:00</span>
        <span>4:00</span>
        <span>5:00</span>
      </div>
      <!-- 技能时间点 -->
      <div
        v-for="(event, index) in safeEvents"
        :key="event.id || index"
        class="absolute top-6 w-2 h-12 rounded-md"
        :class="
          event.state === 'interrupted' ? 'bg-red-500' :
          event.auto_attack ? 'bg-yellow-500' : 'bg-[#165DFF]'
        "
        :style="{ left: getPosition(event.cast_time) + '%' }"
      >
        <div class="absolute -bottom-6 -left-8 w-20 text-[8px] text-center text-[#909399] truncate">
          {{ event.skill_name || '未知技能' }}
        </div>
      </div>
      <!-- 基线 -->
      <div class="absolute top-6 left-0 right-0 h-px bg-[#3a3a3e]" />
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
