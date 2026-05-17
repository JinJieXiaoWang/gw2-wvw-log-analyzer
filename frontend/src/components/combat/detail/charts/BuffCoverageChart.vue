<script setup lang="ts">
/**
 * Buff 覆盖率图表组件
 * 功能：展示团队 Buff 覆盖情况
 * 更新：2026-05-11
 */

import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService';
import { computed } from 'vue';

const props = defineProps<{
  players: EiAnalysisPlayer[]
}>()

const buffStats = computed(() => [
  { label: '威能', key: 'might_uptime', icon: '🔥', color: '#FF4D6A' },
  { label: '激怒', key: 'fury_uptime', icon: '⚡', color: '#FFAA00' },
  { label: '保护', key: 'protection_uptime', icon: '🛡️', color: '#00D68F' },
  { label: '急速', key: 'quickness_uptime', icon: '⏱️', color: '#165DFF' },
  { label: '敏捷', key: 'alacrity_uptime', icon: '⏩', color: '#6366F1' },
  { label: '稳固', key: 'stability_uptime', icon: '🔒', color: '#FF8A65' },
])

const buffCoverage = computed(() => {
  return buffStats.value.map(buff => {
    const values = props.players
      .map(p => Number((p as any)[buff.key]) || 0)
      .filter(v => v > 0)

    const avg = values.length
      ? values.reduce((a, b) => a + b, 0) / values.length
      : 0

    const coverage = props.players.filter(p => (Number((p as any)[buff.key]) || 0) > 0).length
    const coveragePercent = Math.round((coverage / Math.max(props.players.length, 1)) * 100)

    return {
      ...buff,
      avg,
      coveragePercent,
      playersWithBuff: coverage,
    }
  })
})
</script>

<template>
  <div class="card p-6 rounded-xl">
    <h3 class="font-semibold text-neutral-text mb-4">
      Buff 覆盖率
    </h3>
    <div class="space-y-3">
      <div
        v-for="buff in buffCoverage"
        :key="buff.key"
        class="space-y-1"
      >
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-2">
            <span>{{ buff.icon }}</span>
            <span class="text-neutral-text">{{ buff.label }}</span>
            <span class="text-xs text-neutral-text-secondary">
              ({{ buff.playersWithBuff }}/{{ players.length }})
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-neutral-text-secondary">覆盖率</span>
            <span class="font-mono text-neutral-text">{{ buff.coveragePercent }}%</span>
            <span class="font-mono text-neutral-text-secondary">|</span>
            <span class="font-mono text-neutral-text">{{ buff.avg.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="h-2 bg-neutral-bg rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :style="{
              width: buff.coveragePercent + '%',
              backgroundColor: buff.color
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>
