<script setup lang="ts">
/**
 * 战斗统计概览组件
 * 功能：展示团队统计平均数据
 * 更新：2022026-05-11
 */

import { computed } from 'vue'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

const props = defineProps<{
  players: EiAnalysisPlayer[]
}>()

const statAverages = computed(() => {
  const list = props.players
  if (!list.length) return {
    protection: 0,
    stability: 0,
    hitRate: 100,
    skillCastUptime: 0,
    stackDist: 0,
    distToCom: 0
  }

  const sum = (key: keyof EiAnalysisPlayer) => list.reduce((s, p) => s + (Number(p[key]) || 0), 0)

  const avgProtection = list.filter(p => p.protection_uptime > 0)
    .reduce((s, p) => s + p.protection_uptime, 0) / list.filter(p => p.protection_uptime > 0).length || 0

  const avgStability = list.filter(p => p.stability_uptime > 0)
    .reduce((s, p) => s + p.stability_uptime, 0) / list.filter(p => p.stability_uptime > 0).length || 0

  const hitRate = 100 - ((sum('missed') / (sum('missed') + sum('critical_rate') + sum('flanking_rate') + sum('glance_rate') + 1)) * 100) || 0

  const avgSkillCast = list.filter(p => p.skill_cast_uptime > 0)
    .reduce((s, p) => s + p.skill_cast_uptime, 0) / list.filter(p => p.skill_cast_uptime > 0).length || 0

  const avgStackDist = list.filter(p => p.stack_dist > 0)
    .reduce((s, p) => s + p.stack_dist, 0) / list.filter(p => p.stack_dist > 0).length || 0

  const avgDistToCom = list.filter(p => p.dist_to_com > 0)
    .reduce((s, p) => s + p.dist_to_com, 0) / list.filter(p => p.dist_to_com > 0).length || 0

  return {
    protection: avgProtection || 0,
    stability: avgStability || 0,
    hitRate: Math.min(Math.max(hitRate, 0), 100),
    skillCastUptime: avgSkillCast || 0,
    stackDist: avgStackDist || 0,
    distToCom: avgDistToCom || 0,
  }
})

const statList = computed(() => [
  { label: '保护覆盖', value: statAverages.value.protection, unit: '%', icon: 'pi pi-shield', color: '#00D68F', threshold: 70 },
  { label: '稳固覆盖', value: statAverages.value.stability, unit: '%', icon: 'pi pi-lock', color: '#165DFF', threshold: 60 },
  { label: '命中率', value: statAverages.value.hitRate, unit: '%', icon: 'pi pi-check', color: '#FFAA00', threshold: 90 },
  { label: '技能施放', value: statAverages.value.skillCastUptime, unit: '%', icon: 'pi pi-play', color: '#FF4D6A', threshold: 70 },
  { label: '堆叠距离', value: statAverages.value.stackDist, unit: '', icon: 'pi pi-users', color: '#6366F1', threshold: null },
  { label: '指挥距离', value: statAverages.value.distToCom, unit: '', icon: 'pi pi-map-marker', color: '#00B4FF', threshold: null },
])

const getValueColor = (item: typeof statList.value[0]) => {
  if (item.threshold === null) return 'text-neutral-text'
  return item.value >= item.threshold ? 'text-success' : item.value >= item.threshold * 0.6 ? 'text-warning' : 'text-error'
}
</script>

<template>
  <div class="card p-6 rounded-xl">
    <h3 class="font-semibold text-neutral-text mb-4">
      团队统计概览
    </h3>
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div
        v-for="stat in statList"
        :key="stat.label"
        class="text-center p-3 rounded-lg bg-neutral-bg/50 hover:bg-neutral-bg transition-colors"
      >
        <i
          :class="['pi', stat.icon, 'text-lg mb-2']"
          :style="{ color: stat.color }"
        />
        <div
          class="text-lg font-bold"
          :class="getValueColor(stat)"
        >
          {{ stat.value.toFixed(1) }}{{ stat.unit }}
        </div>
        <div class="text-xs text-neutral-text-secondary">
          {{ stat.label }}
        </div>
      </div>
    </div>
  </div>
</template>
