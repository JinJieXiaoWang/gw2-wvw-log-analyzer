<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-status-warning/30 to-status-error/30 flex items-center justify-center">
        <i class="pi pi-exclamation-triangle text-status-warning" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          失误统计
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          需要改进的地方
        </p>
      </div>
    </div>
    <div class="space-y-4">
      <div
        v-for="mistake in mistakeStats"
        :key="mistake.id"
        class="p-4 bg-neutral-bg hover:bg-neutral-hover rounded-xl transition-all"
      >
        <div class="flex items-start justify-between mb-2">
          <div>
            <p class="text-neutral-text font-bold">
              {{ mistake.type }}
            </p>
            <p class="text-xs text-neutral-text-secondary">
              {{ mistake.description }}
            </p>
          </div>
          <span class="game-badge game-badge-error">
            {{ mistake.count }}次
          </span>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex-1 game-progress">
            <div
              class="game-progress-error"
              :style="{ width: (mistake.count / maxMistakeCount * 100) + '%' }"
            />
          </div>
          <span class="text-xs text-neutral-text-disabled font-medium">{{ (mistake.count / maxMistakeCount * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 失误统计组件
 * 功能：显示技能循环中的失误统计
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { computed } from 'vue'

// Props
const props = defineProps<{
  mistakeStats: Array<{
    id: number
    type: string
    description: string
    count: number
  }>
}>()

// 确保props被使用
console.log(props.mistakeStats)

// 计算属性
const maxMistakeCount = computed(() => props.mistakeStats.length > 0 ? Math.max(...props.mistakeStats.map(m => m.count)) : 0)
</script>