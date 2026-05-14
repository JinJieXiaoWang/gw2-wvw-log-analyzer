<template>
  <div class="bg-gray-800 rounded-lg p-4" :class="{ 'opacity-50': disabled }">
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
      v-else-if="!suggestionsData || suggestionsData.suggestions.length === 0"
      class="text-center py-8 text-gray-400"
    >
      <p>暂无优化建议</p>
      <p class="text-sm mt-2 text-gray-500">配置AI后可获取智能优化建议</p>
    </div>
    <div
      v-else
      class="space-y-4"
    >
      <div 
        v-for="(suggestion, index) in suggestionsData.suggestions" 
        :key="index" 
        class="bg-gray-700 rounded p-4"
      >
        <div class="flex justify-between items-start">
          <h3 class="font-medium text-gray-200">
            {{ suggestion }}
          </h3>
        </div>
      </div>
      
      <div v-if="suggestionsData.high_priority && suggestionsData.high_priority.length > 0" class="mt-4">
        <h3 class="text-sm font-medium text-red-400 mb-2">高优先级建议</h3>
        <ul class="space-y-2">
          <li 
            v-for="(item, index) in suggestionsData.high_priority" 
            :key="index"
            class="text-sm text-gray-300 flex items-start gap-2"
          >
            <span class="text-red-400">!</span>
            {{ item }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI优化建议组件
 * 功能：显示AI生成的优化建议
 * 作者：System
 * 创建日期：2026-04-27
 * 更新日期：2026-05-20 - 修复数据结构不匹配问题
 */

interface SuggestionsData {
  suggestions: string[]
  high_priority?: string[]
  _metadata?: unknown
}

defineProps<{
  suggestionsData: SuggestionsData | null
  loading: boolean
  disabled?: boolean
}>()
</script>