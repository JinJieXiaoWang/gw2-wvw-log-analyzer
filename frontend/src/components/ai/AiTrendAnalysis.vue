<template>
  <div class="bg-gray-800 rounded-lg p-4">
    <h2 class="text-xl font-semibold mb-4">
      AI趋势分析
    </h2>
    <div
      v-if="loading"
      class="flex justify-center py-8"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
    </div>
    <div
      v-else-if="trend.length === 0"
      class="text-center py-8 text-gray-400"
    >
      暂无趋势数据
    </div>
    <div
      v-else
      class="h-64"
    >
      <!-- 这里可以添加图表组件 -->
      <div class="grid grid-cols-4 gap-4">
        <div
          v-for="(item, index) in trend"
          :key="index"
          class="bg-gray-700 rounded p-3 text-center"
        >
          <p class="text-sm text-gray-400">
            {{ item.period }}
          </p>
          <p class="text-lg font-semibold">
            {{ item.metrics.averagePerformance.toFixed(2) }}
          </p>
          <p class="text-xs text-gray-400">
            {{ item.metrics.totalFights }} 场战斗
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI趋势分析组件
 * 功能：显ʾAI生成的趋势分析数据
 * 作者：˧姐姐
 * 创建日期：2026-04-27
 */

import type { AiTrend } from '@/services/ai/aiService'

defineProps<{
  trend: AiTrend[]
  loading: boolean
}>()
</script>