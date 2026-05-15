<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <MetricCard
      label="总日志"
      :value="totalCount"
      icon="pi pi-file"
      icon-color="text-secondary"
      card-class="card-legendary"
      :animation-delay="0.1"
    >
      <template #extra>
        <i class="pi pi-arrow-up text-status-success text-sm" />
        <span class="text-status-success text-sm">+{{ todayCount }} 今日</span>
      </template>
    </MetricCard>

    <MetricCard
      label="已解析"
      :value="completedCount"
      icon="pi pi-check-circle"
      icon-color="text-status-success"
      card-class="card-exotic"
      icon-bg-class="bg-status-success/20"
      :animation-delay="0.2"
    >
      <template #extra>
        <span class="text-status-success text-sm">{{ completedPercentage }}%</span>
      </template>
    </MetricCard>

    <MetricCard
      label="解析中"
      :value="parsingCount"
      icon="pi pi-spin pi-spinner"
      icon-color="text-status-warning"
      card-class="card-rare"
      icon-bg-class="bg-status-warning/20"
      :animation-delay="0.3"
    >
      <template #extra>
        <span class="text-status-warning text-sm">进行中</span>
      </template>
    </MetricCard>

    <MetricCard
      label="待处理"
      :value="pendingCount"
      icon="pi pi-clock"
      icon-color="text-neutral-text-secondary"
      card-class="card-rare"
      icon-bg-class="bg-neutral-bg"
      :animation-delay="0.4"
    >
      <template #extra>
        <span class="text-neutral-text-secondary text-sm">准备就绪</span>
      </template>
    </MetricCard>
  </div>
</template>

<script setup lang="ts">
/**
 * 日志统计卡片组件
 * 功能：显示日志统计信息
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { computed } from 'vue'
import MetricCard from '@/components/common/feedback/MetricCard.vue'
import { ParseStatus } from '@/constants/dictValues'

// Props
const props = defineProps<{
  logs: Array<{
    status: string
    uploadTime?: string
  }>
  totalRecords?: number
}>()

// 计算属性
const totalCount = computed(() => props.totalRecords ?? props.logs.length)
const completedCount = computed(() => props.logs.filter(l => l.status === ParseStatus.COMPLETED).length)
const parsingCount = computed(() => props.logs.filter(l => l.status === ParseStatus.PARSING).length)
const pendingCount = computed(() => props.logs.filter(l => l.status === ParseStatus.PENDING).length)

/**
 * 动态计算今日新增日志数量
 * 计算逻辑：获取uploadTime为今天的日志数量
 */
const todayCount = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return props.logs.filter(log => {
    if (!log.uploadTime) return false
    try {
      const uploadDate = new Date(log.uploadTime)
      return uploadDate >= today
    } catch {
      return false
    }
  }).length
})

/**
 * 计算已解析百分比
 * 修复：当logs为空时显示0%而非NaN
 */
const completedPercentage = computed(() => {
  if (props.logs.length === 0) {
    return 0
  }
  return Math.round((completedCount.value / props.logs.length) * 100)
})
</script>
