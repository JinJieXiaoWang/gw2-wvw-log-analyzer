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
        <Button
          v-for="m in metricOptions"
          :key="m.value"
          :label="m.label"
          size="small"
          :class="metric === m.value ? 'btn-game' : 'btn-ghost'"
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

import { computed } from 'vue'
import Button from 'primevue/button'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
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

const metricOptions = [
  { label: '伤害', value: 'damage' },
  { label: '治疗', value: 'healing' },
  { label: '场次', value: 'fights' },
  { label: '活跃', value: 'active_accounts' },
]

const metricColors: Record<string, string> = {
  damage: '#ef4444',
  healing: '#22c55e',
  fights: '#3b82f6',
  active_accounts: '#a855f7',
}

const metricLabels: Record<string, string> = {
  damage: '总伤害',
  healing: '总治疗',
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
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(148, 163, 184, 0.2)',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const p = params[0]
        const val = formatNumber(p.value)
        return `<div style="font-weight:600">${p.name}</div><div style="color:${color}">${label}: ${val}</div>`
      }
    },
    grid: { left: 60, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
      axisLabel: { color: '#94a3b8', fontSize: 11, rotate: 30, interval: 'auto' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 11,
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
