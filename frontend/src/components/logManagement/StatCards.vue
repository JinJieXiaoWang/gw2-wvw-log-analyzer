<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    <div
      class="card-legendary animate-slide-in-up"
      style="animation-delay: 0.1s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            总日志
          </p>
          <p class="text-3xl font-bold game-number-legendary">
            {{ totalCount }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <i class="pi pi-arrow-up text-status-success text-sm" />
            <span class="text-status-success text-sm">+{{ todayCount }} 今日</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-gradient-to-br from-secondary/30 to-primary/30 rounded-xl flex items-center justify-center">
          <i class="pi pi-file text-secondary text-2xl" />
        </div>
      </div>
    </div>

    <div
      class="card-exotic animate-slide-in-up"
      style="animation-delay: 0.2s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            已解析
          </p>
          <p class="text-3xl font-bold game-number">
            {{ completedCount }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <span class="text-status-success text-sm">{{ completedPercentage }}%</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-status-success/20 rounded-xl flex items-center justify-center">
          <i class="pi pi-check-circle text-status-success text-2xl" />
        </div>
      </div>
    </div>

    <div
      class="card-rare animate-slide-in-up"
      style="animation-delay: 0.3s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            解析中
          </p>
          <p class="text-3xl font-bold game-number">
            {{ parsingCount }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <span class="text-status-warning text-sm">进行中</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-status-warning/20 rounded-xl flex items-center justify-center">
          <i class="pi pi-spin pi-spinner text-status-warning text-2xl" />
        </div>
      </div>
    </div>

    <div
      class="card-rare animate-slide-in-up"
      style="animation-delay: 0.4s"
    >
      <div class="flex items-center justify-between">
        <div>
          <p class="text-neutral-text-secondary text-sm mb-1">
            待处理
          </p>
          <p class="text-3xl font-bold game-number">
            {{ pendingCount }}
          </p>
          <div class="flex items-center gap-1 mt-2">
            <span class="text-neutral-text-secondary text-sm">准备就绪</span>
          </div>
        </div>
        <div class="w-12 h-12 bg-neutral-bg rounded-xl flex items-center justify-center">
          <i class="pi pi-clock text-neutral-text-secondary text-2xl" />
        </div>
      </div>
    </div>
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
const completedCount = computed(() => props.logs.filter(l => l.status === 'completed').length)
const parsingCount = computed(() => props.logs.filter(l => l.status === 'parsing').length)
const pendingCount = computed(() => props.logs.filter(l => l.status === 'pending').length)

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