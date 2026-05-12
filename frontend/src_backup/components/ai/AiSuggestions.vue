<template>
  <div class="bg-gray-800 rounded-lg p-4">
    <h2 class="text-xl font-semibold mb-4">
      AI优化建议
    </h2>
    <div
      v-if="loading"
      class="flex justify-center py-8"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
    </div>
    <div
      v-else-if="suggestions.length === 0"
      class="text-center py-8 text-gray-400"
    >
      暂无优化建议
    </div>
    <div
      v-else
      class="space-y-4"
    >
      <div 
        v-for="suggestion in suggestions" 
        :key="suggestion.id" 
        class="bg-gray-700 rounded p-4"
      >
        <div class="flex justify-between items-start">
          <h3 class="font-medium">
            {{ suggestion.title }}
          </h3>
          <span 
            class="text-xs px-2 py-1 rounded" 
            :class="{
              'bg-red-900 text-red-200': suggestion.priority === 'high',
              'bg-yellow-900 text-yellow-200': suggestion.priority === 'medium',
              'bg-green-900 text-green-200': suggestion.priority === 'low'
            }"
          >
            {{ suggestion.priority }}
          </span>
        </div>
        <p class="text-sm text-gray-400 mt-1">
          {{ suggestion.description }}
        </p>
        <div class="mt-2 text-sm">
          <strong>建议：</strong> {{ suggestion.recommendation }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI优化建议组件
 * 功能：显ʾAI生成的优化建议
 * 作者：˧姐姐
 * 创建日期：2026-04-27
 */

import type { AiSuggestion } from '@/api/ai/ai'

defineProps<{
  suggestions: AiSuggestion[]
  loading: boolean
}>()
</script>