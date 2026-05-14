<template>
  <div class="bg-gray-800 rounded-lg p-4" :class="{ 'opacity-50': disabled }">
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
      v-else-if="!trendData || trendData.data_points === 0"
      class="text-center py-8 text-gray-400"
    >
      <p>暂无趋势数据</p>
      <p class="text-sm mt-2 text-gray-500">配置AI后可获取趋势分析</p>
    </div>
    <div
      v-else
      class="space-y-4"
    >
      <div class="grid grid-cols-4 gap-4">
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">总战斗场数</p>
          <p class="text-lg font-semibold text-blue-400">
            {{ trendData.data_points || 0 }}
          </p>
        </div>
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">总伤害量</p>
          <p class="text-lg font-semibold text-red-400">
            {{ formatNumber(trendData.total_damage || 0) }}
          </p>
        </div>
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">总击杀数</p>
          <p class="text-lg font-semibold text-green-400">
            {{ trendData.total_kills || 0 }}
          </p>
        </div>
        <div class="bg-gray-700 rounded p-3 text-center">
          <p class="text-sm text-gray-400">平均时长</p>
          <p class="text-lg font-semibold text-yellow-400">
            {{ formatDuration(trendData.avg_duration || 0) }}
          </p>
        </div>
      </div>
      
      <div v-if="trendData.insights && trendData.insights.length > 0" class="mt-4">
        <h3 class="text-sm font-medium text-gray-300 mb-2">分析洞察</h3>
        <ul class="space-y-2">
          <li 
            v-for="(insight, index) in trendData.insights" 
            :key="index"
            class="text-sm text-gray-400 flex items-start gap-2"
          >
            <span class="text-blue-400">•</span>
            {{ insight }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI趋势分析组件
 * 功能：显示AI生成的趋势分析数据
 * 作者：System
 * 创建日期：2026-04-27
 * 更新日期：2026-05-20 - 修复数据结构不匹配问题
 */

interface TrendData {
  data_points?: number
  total_damage?: number
  total_kills?: number
  avg_duration?: number
  trend?: string
  predictions?: unknown[]
  anomalies?: unknown[]
  insights?: string[]
  _metadata?: unknown
}

defineProps<{
  trendData: TrendData | null
  loading: boolean
  disabled?: boolean
}>()

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>