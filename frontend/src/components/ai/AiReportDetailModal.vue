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
                    <SvgIcon
                      :icon="getTypeIcon(report.report_type)"
                      :size="ICON_SIZE_LARGE"
                      :class="getTypeText(report.report_type)"
                    />
                  </div>
                  <div>
                    <h2 class="text-xl font-bold text-white">
                      {{ report.summary || REPORT_TITLE_PLACEHOLDER }}
                    </h2>
                    <span
                      class="text-xs px-2 py-0.5 rounded-full"
                      :class="getTypeBadge(report.report_type)"
                    >
                      {{ getTypeLabel(report.report_type) }}{{ TYPE_LABEL_SUFFIX }}
                    </span>
                  </div>
                </div>
                <p class="text-sm text-gray-400">
                  {{ report.created_at }}
                </p>
              </div>
              <button
                class="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                @click="$emit('close')"
              >
                <SvgIcon
                  icon="x"
                  :size="ICON_SIZE_LARGE"
                  class="text-gray-400 hover:text-white"
                />
              </button>
            </div>
          </div>

          <!-- 内容区域 -->
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            <!-- 报告摘要 -->
            <div class="bg-gray-700/50 rounded-xl p-4 mb-6">
              <div class="flex items-center gap-2 mb-3">
                <SvgIcon
                  icon="file-text"
                  :size="ICON_SIZE_MEDIUM"
                  class="text-blue-400"
                />
                <h3 class="text-sm font-semibold text-gray-200">
                  {{ SECTION_TITLE_SUMMARY }}
                </h3>
              </div>
              <p class="text-gray-300 text-sm leading-relaxed">
                {{ report.summary || SUMMARY_EMPTY_TEXT }}
              </p>
            </div>

            <!-- 分析指标 -->
            <div
              v-if="report.ai_score !== undefined"
              class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
            >
              <div class="bg-gradient-to-br from-gray-700/50 to-gray-800/50 rounded-xl p-4 border border-gray-600/50">
                <p class="text-xs text-gray-400 mb-1">
                  {{ METRIC_LABEL_AI_SCORE }}
                </p>
                <p class="text-xl font-bold text-white">
                  {{ report.ai_score }}
                </p>
              </div>
            </div>

            <!-- 详细分析 -->
            <div class="space-y-4">
              <div class="flex items-center gap-2 mb-3">
                <SvgIcon
                  icon="bar-chart-2"
                  :size="ICON_SIZE_MEDIUM"
                  class="text-green-400"
                />
                <h3 class="text-sm font-semibold text-gray-200">
                  {{ SECTION_TITLE_DETAIL }}
                </h3>
              </div>

              <div
                v-if="parseContent(report)?.detailedAnalysis"
                class="space-y-3"
              >
                <div
                  v-for="(section, index) in parseContent(report)?.detailedAnalysis"
                  :key="index"
                  class="bg-gray-700/30 rounded-xl p-4 border border-gray-600/30"
                >
                  <div class="flex items-center gap-2 mb-2">
                    <SvgIcon
                      icon="chevron-right"
                      :size="ICON_SIZE_SMALL"
                      class="text-blue-400"
                    />
                    <span class="text-sm font-medium text-gray-200">{{ section.title }}</span>
                  </div>
                  <p class="text-sm text-gray-400 pl-6">
                    {{ section.content }}
                  </p>
                </div>
              </div>
              <div
                v-else-if="report.content"
                class="space-y-3"
              >
                <div class="bg-gray-700/30 rounded-xl p-4 border border-gray-600/30">
                  <p class="text-sm text-gray-300 whitespace-pre-wrap">
                    {{ report.content }}
                  </p>
                </div>
              </div>

              <div
                v-else
                class="text-center py-8"
              >
                <div class="inline-flex items-center justify-center p-4 bg-gray-700/50 rounded-xl mb-4">
                  <SvgIcon
                    icon="file-text"
                    :size="ICON_SIZE_XLARGE"
                    class="text-gray-500"
                  />
                </div>
                <p class="text-gray-400">
                  {{ DETAIL_EMPTY_TEXT }}
                </p>
              </div>
            </div>

            <!-- 优化建议 -->
            <div
              v-if="parseContent(report)?.suggestions?.length"
              class="mt-6 space-y-4"
            >
              <div class="flex items-center gap-2 mb-3">
                <SvgIcon
                  icon="lightbulb"
                  :size="ICON_SIZE_MEDIUM"
                  class="text-yellow-400"
                />
                <h3 class="text-sm font-semibold text-gray-200">
                  {{ SECTION_TITLE_SUGGESTIONS }}
                </h3>
              </div>

              <div class="space-y-2">
                <div
                  v-for="(suggestion, index) in parseContent(report)?.suggestions"
                  :key="index"
                  class="flex items-start gap-3 bg-gradient-to-r from-yellow-900/20 to-orange-900/20 rounded-xl p-4 border border-yellow-700/30"
                >
                  <div class="p-1.5 bg-yellow-500/20 rounded-lg flex-shrink-0">
                    <SvgIcon
                      icon="sparkles"
                      :size="ICON_SIZE_SMALL"
                      class="text-yellow-400"
                    />
                  </div>
                  <p class="text-sm text-gray-300">
                    {{ suggestion }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部操作 -->
          <div class="bg-gray-700/50 px-6 py-4 border-t border-gray-700 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <SvgIcon
                icon="download"
                :size="ICON_SIZE_MEDIUM"
                class="text-gray-400"
              />
              <span class="text-sm text-gray-400">{{ REPORT_ID_PREFIX }}{{ report.id }}</span>
            </div>
            <div class="flex items-center gap-3">
              <button
                class="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors"
                @click="exportReport"
              >
                <SvgIcon
                  icon="download"
                  :size="ICON_SIZE_MEDIUM"
                  class="text-gray-300"
                />
                <span class="text-sm text-gray-300">导出报告</span>
              </button>
              <button
                class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                @click="$emit('close')"
              >
                <SvgIcon
                  icon="x"
                  :size="ICON_SIZE_MEDIUM"
                />
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

// ============ 常量定义 ============
// 文案常量
const REPORT_TITLE_PLACEHOLDER = 'AI分析报告'
const TYPE_LABEL_SUFFIX = '分析报告'
const SUMMARY_EMPTY_TEXT = '暂无摘要信息'
const SECTION_TITLE_SUMMARY = '报告摘要'
const METRIC_LABEL_AI_SCORE = 'AI评分'
const SECTION_TITLE_DETAIL = '详细分析'
const DETAIL_EMPTY_TEXT = '暂无详细分析内容'
const SECTION_TITLE_SUGGESTIONS = '优化建议'
const REPORT_ID_PREFIX = '报告ID: '
const EXPORT_ALERT_TEXT = '报告导出功能开发中'

// 图标尺寸常量
const ICON_SIZE_SMALL = 14
const ICON_SIZE_MEDIUM = 16
const ICON_SIZE_LARGE = 20
const ICON_SIZE_XLARGE = 32

// 数值格式化常量
const SCORE_DIVISOR_MILLION = 1000000
const SCORE_DIVISOR_THOUSAND = 1000
const SCORE_DECIMAL_PLACES = 1
const SCORE_SUFFIX_MILLION = 'M'
const SCORE_SUFFIX_THOUSAND = 'K'

// 报告类型映射常量
const REPORT_TYPE_ICONS: Record<string, string> = {
  'fight': 'swords',
  'player': 'user',
  'build': 'code'
}
const REPORT_TYPE_BG_CLASSES: Record<string, string> = {
  'fight': 'bg-red-500/20',
  'player': 'bg-green-500/20',
  'build': 'bg-blue-500/20'
}
const REPORT_TYPE_TEXT_CLASSES: Record<string, string> = {
  'fight': 'text-red-400',
  'player': 'text-green-400',
  'build': 'text-blue-400'
}
const REPORT_TYPE_BADGE_CLASSES: Record<string, string> = {
  'fight': 'bg-red-500/20 text-red-400',
  'player': 'bg-green-500/20 text-green-400',
  'build': 'bg-blue-500/20 text-blue-400'
}
const REPORT_TYPE_LABELS: Record<string, string> = {
  'fight': '战斗',
  'player': '玩家',
  'build': 'Build'
}

// 指标标签映射常量
const METRIC_LABELS: Record<string, string> = {
  'total_damage': '总伤害',
  'damage_per_second': '秒伤',
  'healing': '治疗量',
  'kills': '击杀数',
  'deaths': '死亡数',
  'duration': '战斗时长',
  'efficiency': '效率',
  'score': '评分'
}

// 默认值常量
const DEFAULT_ICON = 'file-text'
const DEFAULT_BG_CLASS = 'bg-gray-500/20'
const DEFAULT_TEXT_CLASS = 'text-gray-400'
const DEFAULT_BADGE_CLASS = 'bg-gray-500/20 text-gray-400'
const DEFAULT_TYPE_LABEL = '未知'
// =================================

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
  return REPORT_TYPE_ICONS[type] || DEFAULT_ICON
}

const getTypeBg = (type: string) => {
  return REPORT_TYPE_BG_CLASSES[type] || DEFAULT_BG_CLASS
}

const getTypeText = (type: string) => {
  return REPORT_TYPE_TEXT_CLASSES[type] || DEFAULT_TEXT_CLASS
}

const getTypeBadge = (type: string) => {
  return REPORT_TYPE_BADGE_CLASSES[type] || DEFAULT_BADGE_CLASS
}

const getTypeLabel = (type: string) => {
  return REPORT_TYPE_LABELS[type] || DEFAULT_TYPE_LABEL
}

const getMetricLabel = (key: string) => {
  return METRIC_LABELS[key] || key.replace('_', ' ')
}

const formatMetricValue = (value: unknown): string => {
  if (typeof value === 'number') {
    if (value >= SCORE_DIVISOR_MILLION) {
      return (value / SCORE_DIVISOR_MILLION).toFixed(SCORE_DECIMAL_PLACES) + SCORE_SUFFIX_MILLION
    } else if (value >= SCORE_DIVISOR_THOUSAND) {
      return (value / SCORE_DIVISOR_THOUSAND).toFixed(SCORE_DECIMAL_PLACES) + SCORE_SUFFIX_THOUSAND
    }
    return value.toString()
  }
  return String(value)
}

const exportReport = () => {
  alert(EXPORT_ALERT_TEXT)
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
