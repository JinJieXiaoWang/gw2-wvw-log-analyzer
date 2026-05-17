<template>
  <div
    class="space-y-6"
    :class="{ 'opacity-50': disabled }"
  >
    <!-- 加载状态 -->
    <div
      v-if="loading"
      class="flex flex-col items-center justify-center py-12"
    >
      <div class="relative w-16 h-16 mb-4">
        <div class="absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full animate-pulse opacity-30" />
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
      <p class="text-gray-400 text-sm">
        {{ STATUS_TEXT.LOADING }}
      </p>
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="!trendData || trendData.data_points === 0"
      class="text-center py-12"
    >
      <div class="inline-flex items-center justify-center p-4 bg-gray-700/50 rounded-xl mb-4">
        <SvgIcon
          icon="trending-up"
          :size="32"
          class="text-gray-500"
        />
      </div>
      <p class="text-gray-400 mb-2">
        {{ STATUS_TEXT.EMPTY_TITLE }}
      </p>
      <p class="text-sm text-gray-500">
        {{ STATUS_TEXT.EMPTY_HINT }}
      </p>
    </div>

    <!-- 趋势数据 -->
    <div
      v-else
      class="space-y-6"
    >
      <!-- 统计卡片 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-900/30 to-gray-800/30 rounded-xl p-4 border border-blue-700/30 hover:border-blue-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon
              icon="bar-chart-2"
              :size="16"
              class="text-blue-400"
            />
            <span class="text-xs text-gray-400">{{ STAT_CARD_LABELS.DATA_POINTS }}</span>
          </div>
          <p class="text-2xl font-bold text-blue-400">
            {{ trendData.data_points || 0 }}
          </p>
        </div>
        
        <div class="bg-gradient-to-br from-red-900/30 to-gray-800/30 rounded-xl p-4 border border-red-700/30 hover:border-red-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon
              icon="swords"
              :size="16"
              class="text-red-400"
            />
            <span class="text-xs text-gray-400">{{ STAT_CARD_LABELS.TOTAL_DAMAGE }}</span>
          </div>
          <p class="text-2xl font-bold text-red-400">
            {{ formatNumber(trendData.total_damage || 0) }}
          </p>
        </div>
        
        <div class="bg-gradient-to-br from-green-900/30 to-gray-800/30 rounded-xl p-4 border border-green-700/30 hover:border-green-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon
              icon="skull"
              :size="16"
              class="text-green-400"
            />
            <span class="text-xs text-gray-400">{{ STAT_CARD_LABELS.TOTAL_KILLS }}</span>
          </div>
          <p class="text-2xl font-bold text-green-400">
            {{ trendData.total_kills || 0 }}
          </p>
        </div>
        
        <div class="bg-gradient-to-br from-yellow-900/30 to-gray-800/30 rounded-xl p-4 border border-yellow-700/30 hover:border-yellow-500/50 transition-all duration-300">
          <div class="flex items-center gap-2 mb-2">
            <SvgIcon
              icon="clock"
              :size="16"
              class="text-yellow-400"
            />
            <span class="text-xs text-gray-400">{{ STAT_CARD_LABELS.AVG_DURATION }}</span>
          </div>
          <p class="text-2xl font-bold text-yellow-400">
            {{ formatDuration(trendData.avg_duration || 0) }}
          </p>
        </div>
      </div>

      <!-- 趋势指示器 -->
      <div
        v-if="trendData.trend"
        class="bg-gradient-to-r from-gray-700/40 to-gray-800/40 rounded-xl p-4 border border-gray-600/50"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div 
              class="p-2 rounded-lg"
              :class="trendIndicatorBgClass"
            >
              <SvgIcon 
                :icon="trendIconName" 
                :size="20" 
                :class="trendIconClass"
              />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-200">
                {{ trendLabel }}
              </p>
              <p class="text-xs text-gray-500">
                {{ STATUS_TEXT.DATA_SOURCE }}
              </p>
            </div>
          </div>
          <div 
            class="px-3 py-1.5 rounded-full text-sm font-medium"
            :class="trendBadgeClass"
          >
            {{ trendBadgeText }}
          </div>
        </div>
      </div>

      <!-- 分析洞察 -->
      <div
        v-if="trendData.insights && trendData.insights.length > 0"
        class="space-y-3"
      >
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-purple-500/20 rounded-lg">
            <SvgIcon
              icon="eye"
              :size="14"
              class="text-purple-400"
            />
          </div>
          <h3 class="text-sm font-semibold text-purple-400">
            {{ SECTION_TITLES.INSIGHTS }}
          </h3>
          <div class="flex-1 h-px bg-gradient-to-r from-purple-500/50 to-transparent" />
        </div>
        
        <div class="space-y-2">
          <div 
            v-for="(insight, index) in trendData.insights" 
            :key="index"
            class="flex items-start gap-3 bg-gray-700/30 rounded-lg p-3 hover:bg-gray-700/50 transition-colors"
          >
            <SvgIcon
              icon="info"
              :size="14"
              class="text-purple-400 flex-shrink-0 mt-0.5"
            />
            <p class="text-sm text-gray-300">
              {{ insight }}
            </p>
          </div>
        </div>
      </div>

      <!-- 异常检测 -->
      <div
        v-if="trendData.anomalies && trendData.anomalies.length > 0"
        class="space-y-3"
      >
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-orange-500/20 rounded-lg">
            <SvgIcon
              icon="alert-circle"
              :size="14"
              class="text-orange-400"
            />
          </div>
          <h3 class="text-sm font-semibold text-orange-400">
            {{ SECTION_TITLES.ANOMALIES }}
          </h3>
          <div class="flex-1 h-px bg-gradient-to-r from-orange-500/50 to-transparent" />
        </div>
        
        <div class="space-y-2">
          <div 
            v-for="(anomaly, index) in trendData.anomalies" 
            :key="index"
            class="flex items-start gap-3 bg-orange-900/20 rounded-lg p-3 border border-orange-700/30"
          >
            <SvgIcon
              icon="alert-triangle"
              :size="14"
              class="text-orange-400 flex-shrink-0 mt-0.5"
            />
            <p class="text-sm text-gray-300">
              {{ formatAnomaly(anomaly) }}
            </p>
          </div>
        </div>
      </div>

      <!-- 预测信息 -->
      <div
        v-if="trendData.predictions && trendData.predictions.length > 0"
        class="space-y-3"
      >
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-cyan-500/20 rounded-lg">
            <SvgIcon
              icon="target"
              :size="14"
              class="text-cyan-400"
            />
          </div>
          <h3 class="text-sm font-semibold text-cyan-400">
            {{ SECTION_TITLES.PREDICTIONS }}
          </h3>
          <div class="flex-1 h-px bg-gradient-to-r from-cyan-500/50 to-transparent" />
        </div>
        
        <div class="bg-gradient-to-r from-cyan-900/20 to-blue-900/20 rounded-xl p-4 border border-cyan-700/30">
          <div class="flex flex-wrap gap-3">
            <div 
              v-for="(prediction, index) in trendData.predictions.slice(0, 3)" 
              :key="index"
              class="flex items-center gap-2 px-3 py-2 bg-gray-700/50 rounded-lg"
            >
              <SvgIcon
                icon="trending-up"
                :size="12"
                class="text-cyan-400"
              />
              <span class="text-sm text-gray-300">{{ formatPrediction(prediction) }}...</span>
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

import { computed } from 'vue'

// === 常量定义 ===
const TREND_DIRECTION = {
  UP: 'up',
  DOWN: 'down',
  STABLE: 'stable',
} as const

const TREND_LABELS: Record<string, string> = {
  [TREND_DIRECTION.UP]: '上升趋势',
  [TREND_DIRECTION.DOWN]: '下降趋势',
  [TREND_DIRECTION.STABLE]: '稳定趋势',
}

const TREND_BADGE_TEXT: Record<string, string> = {
  [TREND_DIRECTION.UP]: '✓ 表现提升',
  [TREND_DIRECTION.DOWN]: '✗ 需要改进',
  [TREND_DIRECTION.STABLE]: '→ 保持稳定',
}

const TREND_STYLE_CLASSES: Record<string, { indicatorBg: string; icon: string; iconText: string; badge: string }> = {
  [TREND_DIRECTION.UP]: {
    indicatorBg: 'bg-green-500/20',
    icon: 'trending-up',
    iconText: 'text-green-400',
    badge: 'bg-green-500/20 text-green-400',
  },
  [TREND_DIRECTION.DOWN]: {
    indicatorBg: 'bg-red-500/20',
    icon: 'trending-down',
    iconText: 'text-red-400',
    badge: 'bg-red-500/20 text-red-400',
  },
  [TREND_DIRECTION.STABLE]: {
    indicatorBg: 'bg-gray-500/20',
    icon: 'minus',
    iconText: 'text-gray-400',
    badge: 'bg-gray-500/20 text-gray-400',
  },
}

const STAT_CARD_LABELS = {
  DATA_POINTS: '战斗场数',
  TOTAL_DAMAGE: '总伤害量',
  TOTAL_KILLS: '总击杀数',
  AVG_DURATION: '平均时长',
} as const

const SECTION_TITLES = {
  INSIGHTS: '分析洞察',
  ANOMALIES: '异常检测',
  PREDICTIONS: 'AI预测',
} as const

const STATUS_TEXT = {
  LOADING: 'AI正在分析战斗趋势...',
  EMPTY_TITLE: '暂无趋势数据',
  EMPTY_HINT: '配置AI后可获取趋势分析',
  DATA_SOURCE: '基于最近战斗数据',
} as const

const NUMBER_THRESHOLDS = {
  MILLION: 1_000_000,
  THOUSAND: 1_000,
} as const

const PREDICTION_MAX_LENGTH = 30
const SECONDS_PER_MINUTE = 60

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

const props = defineProps<{
  trendData: TrendData | null
  loading: boolean
  disabled?: boolean
}>()

const getTrendStyle = (trend: string | undefined) => {
  return TREND_STYLE_CLASSES[trend || ''] || TREND_STYLE_CLASSES[TREND_DIRECTION.STABLE]
}

const trendIndicatorBgClass = computed(() => {
  return getTrendStyle(props.trendData?.trend).indicatorBg
})

const trendIconName = computed(() => {
  return getTrendStyle(props.trendData?.trend).icon
})

const trendIconClass = computed(() => {
  return getTrendStyle(props.trendData?.trend).iconText
})

const trendLabel = computed(() => {
  return TREND_LABELS[props.trendData?.trend || ''] || TREND_LABELS[TREND_DIRECTION.STABLE]
})

const trendBadgeClass = computed(() => {
  return getTrendStyle(props.trendData?.trend).badge
})

const trendBadgeText = computed(() => {
  return TREND_BADGE_TEXT[props.trendData?.trend || ''] || TREND_BADGE_TEXT[TREND_DIRECTION.STABLE]
})

const formatAnomaly = (anomaly: unknown): string => {
  return typeof anomaly === 'string' ? anomaly : JSON.stringify(anomaly)
}

const formatPrediction = (prediction: unknown): string => {
  const text = typeof prediction === 'string' ? prediction : JSON.stringify(prediction)
  return text.substring(0, PREDICTION_MAX_LENGTH)
}

const formatNumber = (num: number): string => {
  if (num >= NUMBER_THRESHOLDS.MILLION) {
    return (num / NUMBER_THRESHOLDS.MILLION).toFixed(1) + 'M'
  } else if (num >= NUMBER_THRESHOLDS.THOUSAND) {
    return (num / NUMBER_THRESHOLDS.THOUSAND).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / SECONDS_PER_MINUTE)
  const secs = Math.floor(seconds % SECONDS_PER_MINUTE)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>
