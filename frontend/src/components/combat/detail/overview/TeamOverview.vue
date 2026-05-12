<script setup lang="ts">
/**
 * 小队概览组件
 * 功能：展示小队分组和 DPS 排行
 * 更新：2026-05-12 - 使用后端预计算数据，移除前端计算逻辑
 */

import type { EiAnalysisGroup, EiAnalysisPlayer } from '@/services/ei/eiAnalysisService';
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers';
import { getProfessionColor, getProfessionIconUrl, getProfessionName } from '@/utils/profession/professionUtils';
import { computed } from 'vue';

const props = defineProps<{
  players: EiAnalysisPlayer[]
  commanders: EiAnalysisPlayer[]
  groups: EiAnalysisGroup[]
  ungroupedPlayers: EiAnalysisPlayer[]
}>()

const topDpsPlayers = computed(() => {
  return [...props.players].sort((a, b) => b.dps - a.dps).slice(0, 10)
})

const getScoreClass = (score: number | null | undefined) => {
  if (score === null || score === undefined) return 'text-neutral-text-secondary'
  if (score >= 80) return 'text-success'
  if (score >= 60) return 'text-warning'
  return 'text-error'
}
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- DPS 排行 -->
    <div class="card p-6 rounded-xl">
      <h3 class="font-semibold text-neutral-text mb-4">
        DPS 排行 TOP10
      </h3>
      <div class="space-y-2">
        <div
          v-for="(player, idx) in topDpsPlayers"
          :key="player.account_name"
          class="flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-bg/50 transition-colors"
        >
          <span
            class="w-6 text-center font-mono text-sm"
            :class="idx < 3 ? 'text-warning font-bold' : 'text-neutral-text-secondary'"
          >
            {{ idx + 1 }}
          </span>
          <img
            :src="getProfessionIconUrl(player.profession)"
            :alt="player.profession"
            class="w-6 h-6 rounded"
          >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-neutral-text truncate">
                {{ player.name || player.account_name }}
              </span>
              <span
                v-if="commanders.some(c => c.account_name === player.account_name)"
                class="px-1.5 py-0.5 text-xs rounded bg-primary/20 text-primary"
              >
                指挥
              </span>
            </div>
            <span
              class="text-xs"
              :style="{ color: getProfessionColor(player.profession) }"
            >
              {{ getProfessionName(player.profession) }}
            </span>
          </div>
          <div class="text-right">
            <div class="text-sm font-mono text-neutral-text">
              {{ fmtCompact(player.dps) }}
            </div>
            <div class="text-xs text-neutral-text-secondary">
              DPS
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 小队列表 -->
    <div class="card p-6 rounded-xl">
      <h3 class="font-semibold text-neutral-text mb-4">
        小队统计
      </h3>
      <div class="space-y-3">
        <div
          v-for="g in groups"
          :key="g.id"
            class="p-3 rounded-lg bg-neutral-bg/50 border border-transparent
                   hover:border-primary/20 transition-all"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span
                class="w-6 h-6 rounded-full bg-primary/20 text-primary text-xs flex items-center
                       justify-center font-bold">
                {{ g.id }}
              </span>
              <span class="text-sm text-neutral-text">小队 {{ g.id }}</span>
              <span class="text-xs text-neutral-text-secondary">({{ g.players.length }}人)</span>
            </div>
            <div class="flex items-center gap-4 text-xs">
              <span class="text-neutral-text-secondary">
                总伤: <span class="text-neutral-text">{{ fmtCompact(g.total_damage) }}</span>
              </span>
              <span class="text-neutral-text-secondary">
                均DPS: <span class="text-neutral-text">{{ fmtCompact(g.avg_dps) }}</span>
              </span>
              <span
                v-if="g.avg_score !== null"
                :class="getScoreClass(g.avg_score)"
              >
                评分: {{ g.avg_score.toFixed(0) }}
              </span>
            </div>
          </div>
          <div class="flex gap-1 flex-wrap">
            <div
              v-for="player in g.players"
              :key="player.account_name"
              class="flex items-center gap-1 px-2 py-1 rounded bg-neutral-card text-xs"
            >
              <img
                :src="getProfessionIconUrl(player.profession)"
                class="w-4 h-4"
              >
              <span class="text-neutral-text-secondary truncate max-w-16">{{ player.name || player.account_name }}</span>
            </div>
          </div>
        </div>

        <div
          v-if="ungroupedPlayers.length"
          class="p-3 rounded-lg bg-neutral-bg/30 border border-dashed border-neutral-border"
        >
          <div class="text-xs text-neutral-text-secondary mb-2">
            未分组 ({{ ungroupedPlayers.length }}人)
          </div>
          <div class="flex gap-1 flex-wrap">
            <div
              v-for="player in ungroupedPlayers"
              :key="player.account_name"
              class="flex items-center gap-1 px-2 py-1 rounded bg-neutral-card text-xs"
            >
              <img
                :src="getProfessionIconUrl(player.profession)"
                class="w-4 h-4"
              >
              <span class="text-neutral-text-secondary truncate max-w-16">{{ player.name || player.account_name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
