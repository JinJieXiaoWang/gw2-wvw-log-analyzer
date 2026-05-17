<template>
  <div
    class="space-y-4"
    :class="{ 'opacity-50': disabled }"
  >
    <!-- 加载状态 -->
    <div
      v-if="loading"
      class="flex flex-col items-center justify-center py-12"
    >
      <div class="relative w-16 h-16 mb-4">
        <div class="absolute inset-0 bg-gradient-to-br from-yellow-500 to-amber-500 rounded-full animate-pulse opacity-30" />
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-8 h-8 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
      <p class="text-gray-400 text-sm">
        AI正在生成优化建议...
      </p>
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="!suggestionsData || suggestionsData.suggestions.length === 0"
      class="text-center py-12"
    >
      <div class="inline-flex items-center justify-center p-4 bg-gray-700/50 rounded-xl mb-4">
        <SvgIcon
          icon="lightbulb"
          :size="32"
          class="text-gray-500"
        />
      </div>
      <p class="text-gray-400 mb-2">
        暂无优化建议
      </p>
      <p class="text-sm text-gray-500">
        配置AI后可获取智能优化建议
      </p>
    </div>

    <!-- 建议列表 -->
    <div
      v-else
      class="space-y-4"
    >
      <!-- 高优先级建议 -->
      <div
        v-if="suggestionsData.high_priority && suggestionsData.high_priority.length > 0"
        class="space-y-3"
      >
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-red-500/20 rounded-lg">
            <SvgIcon
              icon="alert-triangle"
              :size="14"
              class="text-red-400"
            />
          </div>
          <h3 class="text-sm font-semibold text-red-400">
            高优先级建议
          </h3>
          <div class="flex-1 h-px bg-gradient-to-r from-red-500/50 to-transparent" />
        </div>
        
        <div 
          v-for="(item, index) in suggestionsData.high_priority" 
          :key="'high-' + index"
          class="group bg-gradient-to-r from-red-900/20 to-orange-900/20 hover:from-red-900/30 hover:to-orange-900/30 rounded-xl p-4 border border-red-700/30 hover:border-red-500/50 transition-all duration-300"
        >
          <div class="flex items-start gap-3">
            <div class="p-2 bg-red-500/20 rounded-lg flex-shrink-0">
              <SvgIcon
                icon="flame"
                :size="16"
                class="text-red-400"
              />
            </div>
            <div class="flex-1">
              <p class="text-gray-200 leading-relaxed">
                {{ item }}
              </p>
              <div class="mt-3 flex items-center gap-2">
                <button 
                  class="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 text-xs rounded-lg transition-colors"
                  @click="applySuggestion(item)"
                >
                  <SvgIcon
                    icon="zap"
                    :size="12"
                  />
                  <span>立即应用</span>
                </button>
                <button 
                  class="text-xs text-gray-500 hover:text-gray-400 transition-colors"
                  @click="dismissSuggestion(index)"
                >
                  忽略
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 普通建议 -->
      <div class="space-y-3">
        <div class="flex items-center gap-2">
          <div class="p-1.5 bg-blue-500/20 rounded-lg">
            <SvgIcon
              icon="lightbulb"
              :size="14"
              class="text-blue-400"
            />
          </div>
          <h3 class="text-sm font-semibold text-blue-400">
            优化建议
          </h3>
          <div class="flex-1 h-px bg-gradient-to-r from-blue-500/50 to-transparent" />
        </div>
        
        <div 
          v-for="(suggestion, index) in suggestionsData.suggestions" 
          :key="index"
          class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-blue-500/30 transition-all duration-300"
        >
          <div class="flex items-start gap-3">
            <div class="p-2 bg-blue-500/20 rounded-lg flex-shrink-0 group-hover:bg-blue-500/30 transition-colors">
              <SvgIcon
                icon="sparkles"
                :size="16"
                class="text-blue-400"
              />
            </div>
            <div class="flex-1">
              <p class="text-gray-200 leading-relaxed">
                {{ suggestion }}
              </p>
              <div class="mt-3 flex items-center gap-2">
                <button 
                  class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs rounded-lg transition-colors"
                  @click="applySuggestion(suggestion)"
                >
                  <SvgIcon
                    icon="check"
                    :size="12"
                  />
                  <span>采纳建议</span>
                </button>
                <button 
                  class="text-xs text-gray-500 hover:text-gray-400 transition-colors"
                  @click="dismissSuggestion(index)"
                >
                  忽略
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 建议统计 -->
      <div class="pt-4 border-t border-gray-700/50">
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>共 {{ suggestionsData.suggestions.length + (suggestionsData.high_priority?.length || 0) }} 条建议</span>
          <button 
            class="flex items-center gap-1 hover:text-gray-400 transition-colors"
            @click="$emit('refresh')"
          >
            <SvgIcon
              icon="refresh-cw"
              :size="12"
            />
            <span>获取更多建议</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AI优化建议组件
 * 功能：显示AI生成的优化建议，支持一键应用和忽略
 * 作者：System
 * 创建日期：2026-04-27
 * 更新日期：2026-05-20 - 添加智能推荐和一键应用功能
 */

interface SuggestionsData {
  suggestions: string[]
  high_priority?: string[]
  _metadata?: unknown
}

const props = defineProps<{
  suggestionsData: SuggestionsData | null
  loading: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  'apply-suggestion': [suggestion: string]
  'dismiss-suggestion': [index: number]
  'refresh': []
}>()

const applySuggestion = (suggestion: string) => {
  emit('apply-suggestion', suggestion)
}

const dismissSuggestion = (index: number) => {
  emit('dismiss-suggestion', index)
}
</script>