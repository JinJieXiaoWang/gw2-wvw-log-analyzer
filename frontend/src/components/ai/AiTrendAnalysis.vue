<template>
  <div class="space-y-6" :class="{ 'opacity-50': disabled }">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-12">
      <div class="relative w-16 h-16 mb-4">
        <div class="absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full animate-pulse opacity-30" />
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
      <p class="text-gray-400 text-sm">AI正在分析战斗趋势...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!trendData || trendData.data_points === 0" class="text-center py-12">
      <div class="inline-flex items-center justify-center p-4 bg-gray-700/50 rounded-xl mb-4">
        <SvgIcon icon="trending-up" :size="32" class="text-gray-500" />
      </div>
      <p class="text-gray-400 mb-2">暂无趋势数据</p>
      <p class="text-sm text-gray-500">配置AI后可获取趋势分析</p>
    </div>

    <!-- 趋势数据 -->
    <div v-else class="space-y-6">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-900/30 to-gray-800/30 rounded-xl p-4 border border-blue-700/30 hover:border-blue-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon icon="bar-chart-2" :size="16" class="text-blue-400" />
            <span class="text-xs text-gray-400">战斗场数</span>
          </div>
          <p class="text-2xl font-bold text-blue-400">{{ trendData.data_points || 0 }}</p>
        </div>
        
        <div class="bg-gradient-to-br from-red-900/30 to-gray-800/30 rounded-xl p-4 border border-red-700/30 hover:border-red-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon icon="swords" :size="16" class="text-red-400" />
            <span class="text-xs text-gray-400">总伤害量</span>
          </div>
          <p class="text-2xl font-bold text-red-400">{{ formatNumber(trendData.total_damage || 0) }}</p>
        </div>
        
        <div class="bg-gradient-to-br from-green-900/30 to-gray-800/30 rounded-xl p-4 border border-green-700/30 hover:border-green-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon icon="skull" :size="16" class="text-green-400" />
            <span class="text-xs text-gray-400">总击杀数</span>
          </div>
          <p class="text-2xl font-bold text-green-400">{{ trendData.total_kills || 0 }}</p>
        </div>
        
        <div class="bg-gradient-to-br from-yellow-900/30 to-gray-800/30 rounded-xl p-4 border border-yellow-700/30 hover:border-yellow-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon icon="clock" :size="16" class="text-yellow-400" />
            <span class="text-xs text-gray-400">平均时长</span>
          </div>
          <p class="text-2xl font-bold text-yellow-400">{{ formatDuration(trendData.avg_duration || 0) }}</p>
        </div>
      </div>

      <!-- 趋势指示器 -->
      <div v-if="trendData.trend" class="bg-gradient-to-r from-gray-700/40 to-gray-800/40 rounded-xl p-4 border border-gray-600/50">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div 
              class="p-2 rounded-lg"
              :class="trendData.trend === 'up' ? 'bg-green-500/20' : trendData.trend === 'down' ? 'bg-red-500/20' : 'bg-gray-500/20'"
            >
              <SvgIcon 
                :icon="trendData.trend === 'up' ? 'trending-up' : trendData.trend === 'down' ? 'trending-down' : 'minus'" 
                :size="20" 
                :class="trendData.trend === 'up' ? 'text-green-400' : trendData.trend === 'down' ? 'text-red-400' : 'text-gray-400'"
              />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-200">
                {{ trendData.trend === 'up' ? '上升趋势' : trendData.trend === 'down' ? '下降趋势' : '稳定趋势' }}
              </p>
              <p class="text-xs text-gray-500">基于最近战斗数据</p>
            </div>
          </div>
          <div 
            class="px-3 py-1.5 rounded-full text-sm font-medium"
            :class="trendData.trend === 'up' ? 'bg-green-500/20 text-green-400' : trendData.trend === 'down' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'"
          >
            {{ trendData.trend === 'up' ? '✓ 表现提升' : trendData.trend === 'down' ? '✗ 需要改进' : '→ 保持稳定' }}
          </div>
        </div>
      </div>

      <!-- 分析洞察 -->
      <div v-if="trendData.insights && trendData.insights.length > 0" class="space-y-3">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-purple-500/20 rounded-lg">
            <SvgIcon icon="eye" :size="14" class="text-purple-400" />
          </div>
          <h3 class="text-sm font-semibold text-purple-400">分析洞察</h3>
          <div class="flex-1 h-px bg-gradient-to-r from-purple-500/50 to-transparent" />
        </div>
        
        <div class="space-y-2">
          <div 
            v-for="(insight, index) in trendData.insights" 
            :key="index"
            class="flex items-start gap-3 bg-gray-700/30 rounded-lg p-3 hover:bg-gray-700/50 transition-colors"
          >
            <SvgIcon icon="info" :size="14" class="text-purple-400 flex-shrink-0 mt-0.5" />
            <p class="text-sm text-gray-300">{{ insight }}</p>
          </div>
        </div>
      </div>

      <!-- 异常检测 -->
      <div v-if="trendData.anomalies && trendData.anomalies.length > 0" class="space-y-3">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-orange-500/20 rounded-lg">
            <SvgIcon icon="alert-circle" :size="14" class="text-orange-400" />
          </div>
          <h3 class="text-sm font-semibold text-orange-400">异常检测</h3>
          <div class="flex-1 h-px bg-gradient-to-r from-orange-500/50 to-transparent" />
        </div>
        
        <div class="space-y-2">
          <div 
            v-for="(anomaly, index) in trendData.anomalies" 
            :key="index"
            class="flex items-start gap-3 bg-orange-900/20 rounded-lg p-3 border border-orange-700/30"
          >
            <SvgIcon icon="alert-triangle" :size="14" class="text-orange-400 flex-shrink-0 mt-0.5" />
            <p class="text-sm text-gray-300">{{ typeof anomaly === 'string' ? anomaly : JSON.stringify(anomaly) }}</p>
          </div>
        </div>
      </div>

      <!-- 预测信息 -->
      <div v-if="trendData.predictions && trendData.predictions.length > 0" class="space-y-3">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-cyan-500/20 rounded-lg">
            <SvgIcon icon="target" :size="14" class="text-cyan-400" />
          </div>
          <h3 class="text-sm font-semibold text-cyan-400">AI预测</h3>
          <div class="flex-1 h-px bg-gradient-to-r from-cyan-500/50 to-transparent" />
        </div>
        
        <div class="bg-gradient-to-r from-cyan-900/20 to-blue-900/20 rounded-xl p-4 border border-cyan-700/30">
          <div class="flex flex-wrap gap-3">
            <div 
              v-for="(prediction, index) in trendData.predictions.slice(0, 3)" 
              :key="index"
              class="flex items-center gap-2 px-3 py-2 bg-gray-700/50 rounded-lg"
            >
              <SvgIcon icon="trending-up" :size="12" class="text-cyan-400" />
              <span class="text-sm text-gray-300">{{ typeof prediction === 'string' ? prediction : JSON.stringify(prediction).substring(0, 30) }}...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI趋势分析组件
 * 功能：显示AI生成的趋势分析数据，包含统计卡片、趋势指示器、分析洞察和预测
 * 作者：System
 * 创建日期：2026-04-27
 * 更新日期：2026-05-20 - 添加可视化图表和趋势预测功能
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