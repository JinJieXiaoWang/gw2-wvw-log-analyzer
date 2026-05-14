<template>
  <div class="bg-gray-800 rounded-lg p-4" :class="{ 'opacity-50': disabled }">
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
      <p>暂无AI报告</p>
      <p class="text-sm mt-2 text-gray-500">配置AI后可生成分析报告</p>
    </div>
    <div
      v-else
      class="space-y-4"
    >
      <div 
        v-for="report in reports" 
        :key="report.id" 
        class="bg-gray-700 rounded p-4 hover:bg-gray-600 transition-colors cursor-pointer"
        :class="{ 'cursor-not-allowed opacity-70': disabled }"
        @click="!disabled && viewReport(String(report.id))"
      >
        <div class="flex justify-between items-center">
          <h3 class="font-medium">
            {{ report.summary || report.target_type || 'AI分析报告' }}
          </h3>
          <span class="text-xs px-2 py-1 rounded bg-blue-900 text-blue-200">{{ report.report_type }}</span>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          {{ report.created_at }}
        </p>
      </div>
    </div>
    <div class="mt-4 flex justify-center">
      <BaseLoadMore
        v-if="reports.length > 0 && !disabled"
        :load-callback="handleLoadMore"
        :has-more="hasMore"
        :show-no-more="true"
        :show-load-more-button="true"
        :show-loading="true"
        :show-error="true"
        no-more-text="没有更多AI报告了"
        load-more-button-text="加载更多报告"
        @load-more="handleLoadMore"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI报告列表组件
 * 功能：显示AI生成的报告列表，支持滚动加载
 * 作者：System
 * 创建日期：2026-04-27
 * 更新日期：2026-05-11 - 集成BaseLoadMore组件
 * 更新日期：2026-05-20 - 添加disabled状态支持
 */

import BaseLoadMore from '@/components/common/ui/overlay/BaseLoadMore.vue'
import type { AiReport } from '@/services/ai/aiService'

defineProps<{
  reports: AiReport[]
  loading: boolean
  hasMore: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  'view-report': [reportId: string]
  'load-more': []
}>()

const viewReport = (reportId: string) => {
  emit('view-report', reportId)
}

const handleLoadMore = async () => {
  emit('load-more')
}
</script>