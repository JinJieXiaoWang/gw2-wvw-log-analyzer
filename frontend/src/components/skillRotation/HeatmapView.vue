<script setup lang="ts">
// 模块功能：技能热力图视图组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { RotationEvent, SkillStat } from '@/models/skillRotation'
import { computed } from 'vue'

interface Props {
  events?: RotationEvent[] | null
  topSkills?: SkillStat[] | null
  totalDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  events: null,
  topSkills: null,
  totalDuration: 300000
})

const safeEvents = computed(() => {
  if (!Array.isArray(props.events)) return []
  return props.events.filter(event => event !== null && event !== undefined)
})

const safeSkills = computed(() => {
  if (!Array.isArray(props.topSkills)) return []
  return props.topSkills.filter(skill => skill !== null && skill !== undefined)
})

const intervals = computed(() => {
  const safeDuration = props.totalDuration || 300000
  const interval = 30000 // 30秒一个区间
  const count = Math.ceil(safeDuration / interval)
  return Array.from({ length: count }, (_, i) => ({
    index: i,
    start: i * interval,
    end: (i + 1) * interval,
    label: `${i * 0.5}:00`
  }))
})

function getSkillUsageInInterval(skillId: number, start: number, end: number): number {
  return safeEvents.value.filter(e =>
    e &&
    e.skill_id === skillId &&
    e.cast_time !== undefined &&
    e.cast_time >= start &&
    e.cast_time < end
  ).length
}

function getHeatColor(count: number, maxCount: number): string {
  if (maxCount === 0) return 'bg-[#2a2a2e]'
  const intensity = Math.min(count / maxCount, 1)
  if (intensity > 0.75) return 'bg-[#FF7D00]'
  if (intensity > 0.5) return 'bg-[#165DFF]'
  if (intensity > 0.25) return 'bg-[#3a3a3e]'
  return 'bg-[#2a2a2e]'
}
</script>

<template>
  <div class="heatmap-view bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <h3 class="text-white text-sm mb-3 font-medium">
      热力图
    </h3>
    <div
      v-if="safeSkills.length > 0"
      class="overflow-x-auto"
    >
      <table class="w-full text-xs">
        <thead>
          <tr>
            <th class="text-left text-[#909399] pb-2 pr-2">
              技能
            </th>
            <th
              v-for="interval in intervals"
              :key="interval.index"
              class="text-[#909399] pb-2 text-center min-w-8"
            >
              {{ interval.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="skill in safeSkills"
            :key="skill.skill_id"
          >
            <td class="text-white py-1 pr-2">
              <div class="flex items-center gap-2">
                <img
                  v-if="skill.skill_icon"
                  :src="skill.skill_icon"
                  class="w-6 h-6 rounded"
                  alt=""
                >
                <span class="truncate max-w-32">{{ skill.skill_name || '未知技能' }}</span>
              </div>
            </td>
            <td
              v-for="interval in intervals"
              :key="interval.index"
              class="py-1 text-center"
            >
              <div
                class="w-8 h-6 rounded mx-auto flex items-center justify-center"
                :class="getHeatColor(getSkillUsageInInterval(skill.skill_id, interval.start, interval.end), 5)"
              >
                {{ getSkillUsageInInterval(skill.skill_id, interval.start, interval.end) || '' }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-else
      class="text-[#909399] text-center py-8"
    >
      暂无技能数据
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
