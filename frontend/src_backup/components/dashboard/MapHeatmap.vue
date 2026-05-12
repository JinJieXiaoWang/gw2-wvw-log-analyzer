<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.7s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-status-success/30 to-status-warning/30 flex items-center justify-center">
        <i class="pi pi-map-marker text-status-success" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          地图热度
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          各战场出场频次
        </p>
      </div>
    </div>
    <div
      v-if="isLoading"
      class="h-64 flex items-center justify-center text-neutral-text-disabled"
    >
      <i class="pi pi-spin pi-spinner text-3xl" />
    </div>
    <div
      v-else-if="!items?.length"
      class="h-64 flex items-center justify-center text-neutral-text-disabled"
    >
      <span>暂无数据</span>
    </div>
    <v-chart
      v-else
      class="h-64"
      :option="chartOption"
      autoresize
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 地图热度组件 v2.0
 * 功能：ECharts 柱状图展示各地图战斗场次
 * 更新：2026-05-04 - 替代 MapWinRate
 */

import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const props = defineProps<{
  items: Array<{
    map_name: string
    fight_count: number
    avg_duration_sec: number
    total_damage: number
    avg_player_count: number
  }>
  isLoading: boolean
}>()

const chartOption = computed(() => {
  if (!props.items?.length) return {}
  const data = [...props.items].sort((a, b) => b.fight_count - a.fight_count).slice(0, 8)
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(148, 163, 184, 0.2)',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const p = params[0]
        const item = data[p.dataIndex]
        return `<div style="font-weight:600">${p.name}</div>
                <div>战斗场次: ${item.fight_count}</div>
                <div>平均时长: ${Math.floor(item.avg_duration_sec / 60)}分钟</div>
                <div>平均人数: ${item.avg_player_count}人</div>`
      }
    },
    grid: { left: 10, right: 20, top: 10, bottom: 5, containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    yAxis: {
      type: 'category',
      data: data.map(i => i.map_name).reverse(),
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: data.map(i => i.fight_count).reverse(),
      barWidth: 16,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: {
          type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#22c55e' },
            { offset: 1, color: '#10b981' }
          ]
        }
      }
    }]
  }
})
</script>
