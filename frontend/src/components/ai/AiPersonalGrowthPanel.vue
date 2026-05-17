<template>
  <div class="space-y-6">
    <!-- 头部 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-xl">
          <SvgIcon
            icon="trending-up"
            :size="24"
            class="text-emerald-400"
          />
        </div>
        <div>
          <h2 class="text-xl font-bold text-white">
            个人战力成长档案
          </h2>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            六维战力分析 · 公会排名 · 成长轨迹
          </p>
        </div>
      </div>
      <div
        v-if="data?.overall_score !== undefined"
        class="flex items-center gap-2"
      >
        <span class="text-sm text-neutral-text-secondary">综合评分</span>
        <span
          class="text-2xl font-bold"
          :class="getScoreClass(data.overall_score)"
        >{{ data.overall_score }}</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div
      v-if="loading"
      class="space-y-4"
    >
      <div class="h-64 bg-neutral-card-active/50 rounded-xl animate-pulse" />
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="i in 3"
          :key="i"
          class="h-24 bg-neutral-card-active/50 rounded-xl animate-pulse"
        />
      </div>
    </div>

    <div
      v-else-if="error"
      class="p-6 bg-error/10 border border-error/20 rounded-xl text-center"
    >
      <SvgIcon
        icon="alert-circle"
        :size="32"
        class="text-error mx-auto mb-2"
      />
      <p class="text-error">
        {{ error }}
      </p>
    </div>

    <div
      v-else-if="data"
      class="space-y-6"
    >
      <!-- 雷达图 + 百分位 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-neutral-card-active/40 rounded-xl p-4 border border-neutral-border">
          <h3 class="text-sm font-semibold text-white mb-3">
            六维战力雷达
          </h3>
          <v-chart
            class="w-full h-64"
            :option="radarOption"
            autoresize
          />
        </div>
        <div class="bg-neutral-card-active/40 rounded-xl p-4 border border-neutral-border">
          <h3 class="text-sm font-semibold text-white mb-3">
            公会百分位排名
          </h3>
          <div class="space-y-3">
            <div
              v-for="(label, key) in dimLabels"
              :key="key"
              class="flex items-center gap-3"
            >
              <span class="text-xs text-neutral-text-secondary w-20 truncate">{{ label }}</span>
              <div class="flex-1 h-2 bg-neutral-card-active rounded-full overflow-hidden">
                <!-- 动态值，无法使用 Tailwind 静态类 -->
                <div
                  class="h-full rounded-full transition-all duration-700"
                  :class="getPercentileClass(data.percentiles?.[key])"
                  :style="{ width: `${data.percentiles?.[key] || 0}%` }"
                />
              </div>
              <span
                class="text-xs font-mono w-8 text-right"
                :class="getPercentileTextClass(data.percentiles?.[key])"
              >
                {{ data.percentiles?.[key] || 0 }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 趋势卡片 -->
      <div
        v-if="data.trends"
        class="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            整体趋势
          </div>
          <div class="flex items-center gap-2">
            <SvgIcon
              :icon="trendIcon(data.trends.overall)"
              :size="18"
              :class="trendColor(data.trends.overall)"
            />
            <span
              class="font-semibold"
              :class="trendColor(data.trends.overall)"
            >{{ trendText(data.trends.overall) }}</span>
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            DPS趋势
          </div>
          <div class="flex items-center gap-2">
            <SvgIcon
              :icon="trendIcon(data.trends.dps_trend)"
              :size="18"
              :class="trendColor(data.trends.dps_trend)"
            />
            <span
              class="font-semibold"
              :class="trendColor(data.trends.dps_trend)"
            >{{ trendText(data.trends.dps_trend) }}</span>
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            生存趋势
          </div>
          <div class="flex items-center gap-2">
            <SvgIcon
              :icon="trendIcon(data.trends.survival_trend)"
              :size="18"
              :class="trendColor(data.trends.survival_trend)"
            />
            <span
              class="font-semibold"
              :class="trendColor(data.trends.survival_trend)"
            >{{ trendText(data.trends.survival_trend) }}</span>
          </div>
        </div>
        <div class="p-4 bg-neutral-card-active/40 rounded-xl border border-neutral-border">
          <div class="text-xs text-neutral-text-secondary mb-1">
            数据置信度
          </div>
          <div class="text-lg font-semibold text-white">
            {{ data.trends.confidence }}%
          </div>
        </div>
      </div>

      <!-- 建议列表 -->
      <div
        v-if="data.suggestions?.length"
        class="bg-neutral-card-active/40 rounded-xl p-4 border border-neutral-border"
      >
        <h3 class="text-sm font-semibold text-white mb-3">
          AI 成长建议
        </h3>
        <div class="space-y-2">
          <div
            v-for="(s, i) in data.suggestions"
            :key="i"
            class="p-3 rounded-lg"
            :class="suggestionBg(s.category)"
          >
            <div class="flex items-start gap-3">
              <div
                class="mt-0.5 w-1.5 h-1.5 rounded-full shrink-0"
                :class="suggestionDot(s.category)"
              />
              <div>
                <div class="text-sm text-white font-medium">
                  {{ s.message }}
                </div>
                <div
                  v-if="s.actions?.length"
                  class="mt-1.5 flex flex-wrap gap-2"
                >
                  <span
                    v-for="(action, j) in s.actions"
                    :key="j"
                    class="text-xs px-2 py-0.5 bg-black/20 rounded text-neutral-text-secondary"
                  >{{ action }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- LLM增强分析 -->
      <div
        v-if="data.llm_analysis"
        class="bg-gradient-to-r from-primary/10 to-indigo-500/10 rounded-xl p-4 border border-primary/20"
      >
        <h3 class="text-sm font-semibold text-white mb-2 flex items-center gap-2">
          <SvgIcon
            icon="sparkles"
            :size="16"
            class="text-primary"
          />
          AI 深度洞察
        </h3>
        <p class="text-sm text-neutral-text-secondary leading-relaxed">
          {{ data.llm_analysis.narrative }}
        </p>
        <div
          v-if="data.llm_analysis.growth_plan?.length"
          class="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3"
        >
          <div
            v-for="(plan, i) in data.llm_analysis.growth_plan"
            :key="i"
            class="p-3 bg-black/20 rounded-lg"
          >
            <div class="text-xs text-primary font-medium mb-1">
              {{ plan.phase }}
            </div>
            <div class="text-sm text-white">
              {{ plan.focus }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-else
      class="text-center py-12"
    >
      <p class="text-neutral-text-tertiary">
        选择玩家并点击分析生成成长档案
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import type { PersonalGrowthData } from '@/composables/useAiAnalysis'

use([CanvasRenderer, RadarChart, TooltipComponent, LegendComponent])

const props = defineProps<{
  data: PersonalGrowthData | null
  loading: boolean
  error?: string
}>()

const dimLabels: Record<string, string> = {
  damage_output: '输出能力',
  survival: '生存能力',
  support: '辅助贡献',
  buff_management: 'Buff管理',
  cc_control: '控制能力',
  positioning: '站位意识',
}

const radarOption = computed(() => {
  const dims = props.data?.dimension_scores || {}
  const values = Object.keys(dimLabels).map(k => dims[k]?.score || 0)
  return {
    radar: {
      indicator: Object.values(dimLabels).map(name => ({ name, max: 100 })),
      axisName: { color: '#94a3b8', fontSize: 11 },
      splitArea: { areaStyle: { color: ['rgba(99,102,241,0.03)', 'rgba(99,102,241,0.06)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '当前战力',
        areaStyle: { color: 'rgba(99,102,241,0.25)' },
        lineStyle: { color: '#6366f1', width: 2 },
        itemStyle: { color: '#6366f1' },
      }],
    }],
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,23,42,0.95)', borderColor: 'rgba(255,255,255,0.1)', textStyle: { color: '#fff' } },
  }
})

const getScoreClass = (score: number) => score >= 80 ? 'text-status-success' : score >= 60 ? 'text-warning' : 'text-error'
const getPercentileClass = (p: number) => p >= 70 ? 'bg-status-success' : p >= 40 ? 'bg-warning' : 'bg-error'
const getPercentileTextClass = (p: number) => p >= 70 ? 'text-status-success' : p >= 40 ? 'text-warning' : 'text-error'
const trendIcon = (t: string) => t === 'improving' ? 'trending-up' : t === 'declining' ? 'trending-down' : 'minus'
const trendColor = (t: string) => t === 'improving' ? 'text-status-success' : t === 'declining' ? 'text-error' : 'text-neutral-text-secondary'
const trendText = (t: string) => t === 'improving' ? '上升' : t === 'declining' ? '下降' : '平稳'
const suggestionBg = (cat: string) => ({ priority: 'bg-error/10 border border-error/20', encouragement: 'bg-warning/10 border border-warning/20', strength: 'bg-status-success/10 border border-status-success/20' })[cat] || 'bg-neutral-card-active/50'
const suggestionDot = (cat: string) => ({ priority: 'bg-error', encouragement: 'bg-warning', strength: 'bg-status-success' })[cat] || 'bg-neutral-text-secondary'
</script>
