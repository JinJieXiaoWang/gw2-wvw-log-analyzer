<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-ai/20 to-emerald-500/20 rounded-xl">
          <SvgIcon
            icon="trending-up"
            :size="24"
            class="text-ai"
          />
        </div>
        <h2 class="text-xl font-bold text-white">
          战斗趋势分析
        </h2>
      </div>
      <div class="flex items-center gap-2">
        <BaseSelect
          v-model="localTimeRange"
          :options="timeRangeOptions"
          option-label="label"
          option-value="value"
          class="w-32"
          @change="$emit('time-range-change', localTimeRange)"
        />
        <BaseButton
          icon="pi pi-refresh"
          size="small"
          text
          :loading="loading"
          @click="$emit('refresh')"
        >
          <span class="text-sm text-neutral-text-tertiary">刷新</span>
        </BaseButton>
      </div>
    </div>
    <div
      v-if="loading"
      class="h-48 bg-neutral-card-active/50 rounded-xl animate-pulse"
    />
    <div
      v-else-if="data"
      class="space-y-4"
    >
      <!-- 趋势图表 -->
      <div
        v-if="hasTimeSeries"
        class="bg-neutral-card-active/50 rounded-xl p-4 border border-neutral-border"
      >
        <v-chart
          class="w-full h-64"
          :option="chartOption"
          autoresize
        />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="p-4 bg-neutral-card-active/50 rounded-xl">
          <p class="text-sm text-neutral-text-tertiary">
            数据点数
          </p><p class="text-2xl font-bold text-white">
            {{ data.data_points || 0 }}
          </p>
        </div>
        <div class="p-4 bg-neutral-card-active/50 rounded-xl">
          <p class="text-sm text-neutral-text-tertiary">
            总伤害
          </p><p class="text-2xl font-bold text-primary">
            {{ formatNumber(data.total_damage) }}
          </p>
        </div>
        <div class="p-4 bg-neutral-card-active/50 rounded-xl">
          <p class="text-sm text-neutral-text-tertiary">
            击杀/死亡
          </p><p class="text-2xl font-bold text-ai">
            {{ data.total_kills || 0 }}
          </p>
        </div>
        <div class="p-4 bg-neutral-card-active/50 rounded-xl">
          <p class="text-sm text-neutral-text-tertiary">
            趋势
          </p><p
            class="text-2xl font-bold"
            :class="trendClass"
          >
            {{ data.trend || '未知' }}
          </p>
        </div>
      </div>
      <div
        v-if="data.insights?.length"
        class="p-4 bg-neutral-card-active/50 rounded-xl"
      >
        <p class="text-sm text-neutral-text-tertiary mb-2">
          关键洞察
        </p>
        <p
          v-for="(insight, i) in data.insights.slice(0, 3)"
          :key="i"
          class="text-sm text-neutral-text-secondary mb-1"
        >
          {{ insight }}
        </p>
      </div>
    </div>
    <div
      v-else
      class="text-center py-8"
    >
      <p class="text-neutral-text-tertiary">
        暂无趋势数据
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

interface TrendTimePoint {
  date: string
  damage: number
  kills: number
  deaths: number
  duration: number
}

interface TrendData {
  data_points?: number
  total_damage?: number
  total_kills?: number
  avg_duration?: number
  trend?: string
  insights?: string[]
  time_series?: TrendTimePoint[]
}

const props = defineProps<{ data: TrendData | null; loading: boolean; timeRange: string }>()
const emit = defineEmits<{ refresh: []; 'time-range-change': [range: string] }>()

const localTimeRange = ref(props.timeRange)

const timeRangeOptions = [
  { value: '7d', label: '最近7天' },
  { value: '30d', label: '最近30天' },
  { value: '90d', label: '最近90天' },
]

const hasTimeSeries = computed(() => {
  return !!props.data?.time_series && props.data.time_series.length > 1
})

const chartOption = computed(() => {
  const series = props.data?.time_series || []
  const dates = series.map(s => s.date)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,23,42,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' },
    },
    legend: {
      data: ['伤害', '击杀'],
      textStyle: { color: '#94a3b8' },
      bottom: 0,
    },
    grid: { left: 48, right: 16, top: 16, bottom: 32 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
    },
    yAxis: [
      {
        type: 'value',
        name: '伤害',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: { color: '#94a3b8', fontSize: 10, formatter: (v: number) => v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v },
      },
      {
        type: 'value',
        name: '击杀',
        axisLine: { show: false },
        splitLine: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 10 },
      },
    ],
    series: [
      {
        name: '伤害',
        type: 'line',
        data: series.map(s => s.damage),
        smooth: true,
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(99,102,241,0.3)' }, { offset: 1, color: 'rgba(99,102,241,0)' }] } },
        lineStyle: { color: '#6366f1', width: 2 },
        itemStyle: { color: '#6366f1' },
        showSymbol: false,
      },
      {
        name: '击杀',
        type: 'line',
        yAxisIndex: 1,
        data: series.map(s => s.kills),
        smooth: true,
        lineStyle: { color: '#10b981', width: 2 },
        itemStyle: { color: '#10b981' },
        showSymbol: false,
      },
    ],
  }
})

const trendClass = computed(() => {
  if (props.data?.trend === '上升') return 'text-status-success'
  if (props.data?.trend === '下降') return 'text-error'
  return 'text-warning'
})

const formatNumber = (num?: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<script lang="ts">
export default { name: 'AiTrendPanel' }
</script>
