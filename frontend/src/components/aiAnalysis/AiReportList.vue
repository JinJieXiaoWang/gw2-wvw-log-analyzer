<template>
  <div class="bg-gray-800 rounded-lg p-4">
    <h2 class="text-xl font-semibold mb-4">
      AI报告列表
    </h2>
    <div
      v-if="loading"
      class="flex justify-center py-8"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
    </div>
    <div
      v-else-if="reports.length === 0"
      class="text-center py-8 text-gray-400"
    >
      暂无AI报告
    </div>
    <div
      v-else
      class="space-y-4"
    >
      <div 
        v-for="report in reports" 
        :key="report.id" 
        class="bg-gray-700 rounded p-4 hover:bg-gray-600 transition-colors"
        @click="viewReport(report.id)"
      >
        <div class="flex justify-between items-center">
          <h3 class="font-medium">
            {{ report.targetName }}
          </h3>
          <span class="text-xs px-2 py-1 rounded bg-blue-900 text-blue-200">{{ report.type }}</span>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          {{ report.createdAt }}
        </p>
      </div>
    </div>
    <div class="mt-4 flex justify-center">
      <button 
        v-if="hasMore" 
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors" 
        @click="loadMoreReports"
      >
        加载更多
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI报告列表组件
 * 功能：显示AI生成的报告列表
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import type { AiReport } from '@/api/ai/ai'

defineProps<{
  reports: AiReport[]
  loading: boolean
  hasMore: boolean
}>()

// Emits
const emit = defineEmits<{
  'view-report': [reportId: string]
  'load-more': []
}>()

// 事件处理
const viewReport = (reportId: string) => {
  emit('view-report', reportId)
}

const loadMoreReports = () => {
  emit('load-more')
}
</script>