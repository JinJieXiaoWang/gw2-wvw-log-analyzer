<script setup lang="ts">
// 模块功能：技能详情组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { SkillStat } from '@/models/skillRotation'
import { computed } from 'vue'

interface Props {
  topSkills?: SkillStat[] | null
}

const props = withDefaults(defineProps<Props>(), {
  topSkills: null
})

const safeSkills = computed(() => {
  if (!Array.isArray(props.topSkills)) return []
  return props.topSkills.filter(skill => skill !== null && skill !== undefined)
})

function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null || isNaN(num)) return '0'
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function formatPercent(num: number | undefined | null): string {
  if (num === undefined || num === null || isNaN(num)) return '0.0%'
  return num.toFixed(1) + '%'
}
</script>

<template>
  <div class="skill-details bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <h3 class="text-white text-sm mb-3 font-medium">
      技能详情
    </h3>
    <div class="overflow-x-auto">
      <table class="w-full text-xs">
        <thead>
          <tr class="text-[#909399]">
            <th class="text-left pb-2">
              技能
            </th>
            <th class="text-center pb-2">
              次数
            </th>
            <th class="text-center pb-2">
              伤害
            </th>
            <th class="text-center pb-2">
              占比
            </th>
            <th class="text-center pb-2">
              平均施法
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="skill in safeSkills"
            :key="skill.skill_id"
            class="border-t border-[#2a2a2e]"
          >
            <td class="py-2">
              <div class="flex items-center gap-2">
                <img
                  v-if="skill.skill_icon"
                  :src="skill.skill_icon"
                  class="w-7 h-7 rounded"
                  alt=""
                >
                <div
                  v-else
                  class="w-7 h-7 rounded bg-[#3a3a3e] flex items-center justify-center"
                >
                  {{ skill.skill_name?.charAt(0) || '?' }}
                </div>
                <span class="text-white">{{ skill.skill_name || '未知技能' }}</span>
              </div>
            </td>
            <td class="text-center text-white">
              {{ skill.count || 0 }}
            </td>
            <td class="text-center text-white">
              {{ formatNumber(skill.damage) }}
            </td>
            <td class="text-center text-white">
              {{ formatPercent(skill.percent) }}
            </td>
            <td class="text-center text-white">
              {{ ((skill.avg_cast_time || 0) / 1000).toFixed(2) }}s
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-if="safeSkills.length === 0"
      class="text-[#909399] text-center py-8"
    >
      暂无技能数据
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
