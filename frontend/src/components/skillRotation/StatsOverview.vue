<script setup lang="ts">
// 模块功能：技能循环统计概览组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { RotationStats } from '@/models/skillRotation';
import { computed } from 'vue';

interface Props {
  stats?: RotationStats | null
}

const props = withDefaults(defineProps<Props>(), {
  stats: null
})

const safeStats = computed(() => {
  if (!props.stats) {
    return {
      total_casts: 0,
      total_damage: 0,
      avg_dps: 0,
      skill_cast_uptime: 0,
      interrupted_rate: 0,
      auto_attack_rate: 0,
      top_skills: [],
      buff_coverage: {}
    }
  }
  return props.stats
})

function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null || isNaN(num)) return '0'
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
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
  <div class="stats-overview grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
    <div class="stat-card bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4 hover:border-[#165DFF]">
      <div class="text-xs text-[#909399] mb-1">
        总施法次数
      </div>
      <div class="text-2xl font-bold text-white">
        {{ formatNumber(safeStats.total_casts) }}
      </div>
    </div>
    <div class="stat-card bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4 hover:border-[#165DFF]">
      <div class="text-xs text-[#909399] mb-1">
        总伤害
      </div>
      <div class="text-2xl font-bold text-white">
        {{ formatNumber(safeStats.total_damage) }}
      </div>
    </div>
    <div class="stat-card bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4 hover:border-[#165DFF]">
      <div class="text-xs text-[#909399] mb-1">
        平均DPS
      </div>
      <div class="text-2xl font-bold text-white">
        {{ formatNumber(safeStats.avg_dps) }}
      </div>
    </div>
    <div class="stat-card bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4 hover:border-[#165DFF]">
      <div class="text-xs text-[#909399] mb-1">
        施法占比
      </div>
      <div class="text-2xl font-bold text-white">
        {{ formatPercent(safeStats.skill_cast_uptime) }}
      </div>
    </div>
    <div class="stat-card bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4 hover:border-[#165DFF]">
      <div class="text-xs text-[#909399] mb-1">
        打断率
      </div>
      <div class="text-2xl font-bold text-white">
        {{ formatPercent(safeStats.interrupted_rate) }}
      </div>
    </div>
    <div class="stat-card bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4 hover:border-[#165DFF]">
      <div class="text-xs text-[#909399] mb-1">
        平A占比
      </div>
      <div class="text-2xl font-bold text-white">
        {{ formatPercent(safeStats.auto_attack_rate) }}
      </div>
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
