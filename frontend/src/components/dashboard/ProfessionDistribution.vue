<template>
  <div class="card animate-slide-in-up" style="animation-delay: 0.6s">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-secondary/30 to-status-success/30 flex items-center justify-center">
          <i class="pi pi-chart-pie text-secondary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">职业分布</h3>
          <p class="text-xs text-neutral-text-secondary">按最新出场职业统计</p>
        </div>
      </div>
    </div>
    <div v-if="isLoading" class="h-80 flex items-center justify-center text-neutral-text-disabled">
      <i class="pi pi-spin pi-spinner text-3xl" />
    </div>
    <div v-else-if="!items?.length" class="h-80 flex items-center justify-center text-neutral-text-disabled">
      <span>暂无数据</span>
    </div>
    <div v-else class="flex flex-col lg:flex-row items-start gap-5 min-w-0">
      <v-chart class="h-72 sm:h-80 w-full lg:flex-1 min-w-0" :option="chartOption" autoresize />
      <div
        class="w-full lg:w-auto lg:max-w-[16rem] lg:shrink-0 lg:h-80
               grid grid-cols-2 sm:grid-cols-3
               lg:flex lg:flex-col lg:flex-wrap lg:content-start
               gap-x-4 gap-y-1"
      >
        <div
          v-for="(item, idx) in items"
          :key="item.profession"
          class="flex items-center justify-between text-xs py-0.5 gap-2 min-w-0"
        >
          <div class="flex items-center gap-2 min-w-0">
            <span class="w-2 h-2 rounded-full shrink-0" :style="{ backgroundColor: chartColors[idx % chartColors.length] }" />
            <span class="text-neutral-text truncate">{{ getProfessionName(item.profession) }}</span>
          </div>
          <span class="text-neutral-text-secondary shrink-0 tabular-nums text-[11px]">{{ item.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 职业分布图表组件 v3.0
 * 功能：ECharts 饼图 + 职业中文映射
 * 更新：2026-05-05 - 优化响应式布局，消除滚动条，提升空间利用率
 */

import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getProfessionName } from '@/utils/profession/professionUtils'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const props = defineProps<{
  items: Array<{ profession: string; count: number; total_damage: number }>
  isLoading: boolean
}>()

const chartColors = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#a855f7',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1',
  '#14b8a6', '#e11d48', '#8b5cf6', '#10b981', '#f43f5e'
]

const chartOption = computed(() => {
  if (!props.items?.length) return {}
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(148, 163, 184, 0.2)',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        return `<div style="font-weight:600">${params.name}</div>
                <div>出场: ${params.value} 角色</div>
                <div>占比: ${params.percent}%</div>`
      }
    },
    series: [{
      type: 'pie',
      radius: ['42%', '76%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#0f172a',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        scale: true,
        scaleSize: 8,
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: '#e2e8f0'
        }
      },
      animationType: 'scale',
      animationEasing: 'cubicOut',
      animationDuration: 800,
      data: props.items.map((item, idx) => ({
        value: item.count,
        name: getProfessionName(item.profession),
        itemStyle: { color: chartColors[idx % chartColors.length] }
      }))
    }]
  }
})
</script>
