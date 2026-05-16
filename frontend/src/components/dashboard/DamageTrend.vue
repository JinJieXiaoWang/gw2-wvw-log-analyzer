<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
          <i class="pi pi-chart-line text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            趋势分析
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            时间序列数据
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <BaseButton
          v-for="m in metricOptions"
          :key="m.value"
          :label="m.label"
          size="small"
          :variant="metric === m.value ? 'game' : 'ghost'"
          @click="switchMetric(m.value)"
        />
      </div>
    </div>
    <div
      v-if="isLoading"
      class="h-72 flex items-center justify-center text-neutral-text-disabled"
    >
      <i class="pi pi-spin pi-spinner text-3xl" />
    </div>
    <div
      v-else-if="!chartData?.dates?.length"
      class="h-72 flex items-center justify-center text-neutral-text-disabled"
    >
      <span>暂无数据</span>
    </div>
    <v-chart
      v-else
      class="h-72"
      :option="chartOption"
      autoresize
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 趋势图表组件 v2.0
 * 功能：使用 ECharts 展示多指标时间趋势
 * 更新：2026-05-04 - 集成 ECharts + 真实 API
 */

import { DASHBOARD_METRIC_OPTIONS } from '@/constants/dictValues'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { BarChart, LineChart } from 'echarts/charts'
import { DataZoomComponent, GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { useEChartsTheme } from '@/composables/common/useEChartsTheme'
import { computed } from 'vue'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

const props = defineProps<{
  metric: string
  chartData: any
  isLoading: boolean
}>()

const emit = defineEmits<{
  'update:metric': [value: string]
}>()

const metricOptions = DASHBOARD_METRIC_OPTIONS.map(m => ({ label: m.label, value: m.value }))

const metricColors: Record<string, string> = Object.fromEntries(
  DASHBOARD_METRIC_OPTIONS.map(m => [m.value, m.color])
)

const { tooltip, grid, axisLine, axisLabel, splitLine } = useEChartsTheme()

const metricLabels: Record<string, string> = {
  damage: '总伤害',
  downed: '击倒人数',
  fights: '战斗场次',
  active_accounts: '活跃账号',
}

const switchMetric = (value: string) => {
  emit('update:metric', value)
}

const chartOption = computed(() => {
  const data = props.chartData
  if (!data?.dates?.length) return {}

  const color = metricColors[props.metric] || '#3b82f6'
  const label = metricLabels[props.metric] || '数值'

  return {
    tooltip: {
      ...tooltip,
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        const val = formatNumber(p.value)
        return `<div style="font-weight:600">${p.name}</div><div style="color:${color}">${label}: ${val}</div>`
      }
    },
    grid,
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLine,
      axisLabel: { ...axisLabel, rotate: 30, interval: 'auto' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine,
      axisLabel: {
        ...axisLabel,
        formatter: (v: number) => {
          if (v >= 1000000) return (v / 1000000).toFixed(0) + 'M'
          if (v >= 1000) return (v / 1000).toFixed(0) + 'K'
          return v
        }
      }
    },
    series: [{
      name: label,
      type: 'line',
      data: data.values,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color, width: 3 },
      itemStyle: { color },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '40' },
            { offset: 1, color: color + '05' }
          ]
        }
      }
    }]
  }
})

const formatNumber = (num: number): string => {
  if (!num && num !== 0) return '0'
  if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>
