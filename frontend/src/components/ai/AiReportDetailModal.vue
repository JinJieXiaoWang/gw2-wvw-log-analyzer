<template>
  <Teleport to="body">
    <Transition name="fade">
      <div 
        v-if="report"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        @click.self="$emit('close')"
      >
        <div class="bg-gray-800 rounded-2xl border border-gray-700 shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden animate-scale-in">
          <!-- 头部 -->
          <div class="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 border-b border-gray-700">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <div
                    class="p-2 rounded-lg"
                    :class="getTypeBg(report.report_type)"
                  >
                    <SvgIcon :icon="getTypeIcon(report.report_type)" :size="20" :class="getTypeText(report.report_type)" />
                  </div>
                  <div>
                    <h2 class="text-xl font-bold text-white">{{ report.summary || 'AI分析报告' }}</h2>
                    <span
                      class="text-xs px-2 py-0.5 rounded-full"
                      :class="getTypeBadge(report.report_type)"
                    >
                      {{ getTypeLabel(report.report_type) }}分析报告
                    </span>
                  </div>
                </div>
                <p class="text-sm text-gray-400">{{ report.created_at }}</p>
              </div>
              <button 
                @click="$emit('close')"
                class="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <SvgIcon icon="x" :size="20" class="text-gray-400 hover:text-white" />
              </button>
            </div>
          </div>
          
          <!-- 内容区域 -->
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            <!-- 报告摘要 -->
            <div class="bg-gray-700/50 rounded-xl p-4 mb-6">
              <div class="flex items-center gap-2 mb-3">
                <SvgIcon icon="file-text" :size="16" class="text-blue-400" />
                <h3 class="text-sm font-semibold text-gray-200">报告摘要</h3>
              </div>
              <p class="text-gray-300 text-sm leading-relaxed">{{ report.summary || '暂无摘要信息' }}</p>
            </div>
            
            <!-- 分析指标 -->
            <div v-if="report.ai_score !== undefined" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div class="bg-gradient-to-br from-gray-700/50 to-gray-800/50 rounded-xl p-4 border border-gray-600/50">
                <p class="text-xs text-gray-400 mb-1">AI评分</p>
                <p class="text-xl font-bold text-white">{{ report.ai_score }}</p>
              </div>
            </div>
            
            <!-- 详细分析 -->
            <div class="space-y-4">
              <div class="flex items-center gap-2 mb-3">
                <SvgIcon icon="bar-chart-2" :size="16" class="text-green-400" />
                <h3 class="text-sm font-semibold text-gray-200">详细分析</h3>
              </div>
              
              <div v-if="parseContent(report)?.detailedAnalysis" class="space-y-3">
                <div
                  v-for="(section, index) in parseContent(report)?.detailedAnalysis"
                  :key="index"
                  class="bg-gray-700/30 rounded-xl p-4 border border-gray-600/30"
                >
                  <div class="flex items-center gap-2 mb-2">
                    <SvgIcon icon="chevron-right" :size="14" class="text-blue-400" />
                    <span class="text-sm font-medium text-gray-200">{{ section.title }}</span>
                  </div>
                  <p class="text-sm text-gray-400 pl-6">{{ section.content }}</p>
                </div>
              </div>
              <div v-else-if="report.content" class="space-y-3">
                <div class="bg-gray-700/30 rounded-xl p-4 border border-gray-600/30">
                  <p class="text-sm text-gray-300 whitespace-pre-wrap">{{ report.content }}</p>
                </div>
              </div>
              
              <div v-else class="text-center py-8">
                <div class="inline-flex items-center justify-center p-4 bg-gray-700/50 rounded-xl mb-4">
                  <SvgIcon icon="file-text" :size="32" class="text-gray-500" />
                </div>
                <p class="text-gray-400">暂无详细分析内容</p>
              </div>
            </div>
            
            <!-- 优化建议 -->
            <div v-if="parseContent(report)?.suggestions?.length" class="mt-6 space-y-4">
              <div class="flex items-center gap-2 mb-3">
                <SvgIcon icon="lightbulb" :size="16" class="text-yellow-400" />
                <h3 class="text-sm font-semibold text-gray-200">优化建议</h3>
              </div>

              <div class="space-y-2">
                <div
                  v-for="(suggestion, index) in parseContent(report)?.suggestions"
                  :key="index"
                  class="flex items-start gap-3 bg-gradient-to-r from-yellow-900/20 to-orange-900/20 rounded-xl p-4 border border-yellow-700/30"
                >
                  <div class="p-1.5 bg-yellow-500/20 rounded-lg flex-shrink-0">
                    <SvgIcon icon="sparkles" :size="14" class="text-yellow-400" />
                  </div>
                  <p class="text-sm text-gray-300">{{ suggestion }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 底部操作 -->
          <div class="bg-gray-700/50 px-6 py-4 border-t border-gray-700 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <SvgIcon icon="download" :size="16" class="text-gray-400" />
              <span class="text-sm text-gray-400">报告ID: {{ report.id }}</span>
            </div>
            <div class="flex items-center gap-3">
              <button 
                @click="exportReport"
                class="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors"
              >
                <SvgIcon icon="download" :size="16" class="text-gray-300" />
                <span class="text-sm text-gray-300">导出报告</span>
              </button>
              <button 
                @click="$emit('close')"
                class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
              >
                <SvgIcon icon="x" :size="16" />
                <span class="text-sm">关闭</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * AI报告详情弹窗组件
 * 功能：展示AI分析报告的详细内容，支持导出操作
 * 作者：System
 * 创建日期：2026-05-20
 */

import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import type { AiReport } from '@/services/ai/aiService'

interface ReportContent {
  metrics?: Record<string, number>
  detailedAnalysis?: Array<{ title: string; content: string }>
  suggestions?: string[]
  team_strengths?: string[]
  recommendations?: string[]
}

const parseContent = (report: AiReport | null): ReportContent | null => {
  if (!report?.content) return null
  try {
    return JSON.parse(report.content) as ReportContent
  } catch {
    return null
  }
}

defineProps<{
  report: AiReport | null
}>()

const emit = defineEmits<{
  'close': []
}>()

const getTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    'fight': 'swords',
    'player': 'user',
    'build': 'code'
  }
  return icons[type] || 'file-text'
}

const getTypeBg = (type: string) => {
  const colors: Record<string, string> = {
    'fight': 'bg-red-500/20',
    'player': 'bg-green-500/20',
    'build': 'bg-blue-500/20'
  }
  return colors[type] || 'bg-gray-500/20'
}

const getTypeText = (type: string) => {
  const colors: Record<string, string> = {
    'fight': 'text-red-400',
    'player': 'text-green-400',
    'build': 'text-blue-400'
  }
  return colors[type] || 'text-gray-400'
}

const getTypeBadge = (type: string) => {
  const colors: Record<string, string> = {
    'fight': 'bg-red-500/20 text-red-400',
    'player': 'bg-green-500/20 text-green-400',
    'build': 'bg-blue-500/20 text-blue-400'
  }
  return colors[type] || 'bg-gray-500/20 text-gray-400'
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'fight': '战斗',
    'player': '玩家',
    'build': 'Build'
  }
  return labels[type] || '未知'
}

const getMetricLabel = (key: string) => {
  const labels: Record<string, string> = {
    'total_damage': '总伤害',
    'damage_per_second': '秒伤',
    'healing': '治疗量',
    'kills': '击杀数',
    'deaths': '死亡数',
    'duration': '战斗时长',
    'efficiency': '效率',
    'score': '评分'
  }
  return labels[key] || key.replace('_', ' ')
}

const formatMetricValue = (value: unknown): string => {
  if (typeof value === 'number') {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M'
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K'
    }
    return value.toString()
  }
  return String(value)
}

const exportReport = () => {
  alert('报告导出功能开发中')
}
</script>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>