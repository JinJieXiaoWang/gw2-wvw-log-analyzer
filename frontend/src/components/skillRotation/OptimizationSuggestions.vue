<script setup lang="ts">
// 模块功能：优化建议组件
// 作者：帅姐姐
// 创建日期：2026-04-27
// 更新日期：2026-05-14

import type { OptimizationSuggestion } from '@/models/skillRotation';
import { computed } from 'vue';

interface Props {
  suggestions?: OptimizationSuggestion[] | null
}

const props = withDefaults(defineProps<Props>(), {
  suggestions: null
})

const safeSuggestions = computed(() => {
  if (!Array.isArray(props.suggestions)) return []
  return props.suggestions.filter(suggestion => suggestion !== null && suggestion !== undefined)
})
</script>

<template>
  <div class="optimization-suggestions bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <div class="flex items-center gap-3 mb-4">
      <div
        class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#165DFF]/30 to-green-500/30 flex items-center justify-center"
      >
        <i class="pi pi-lightbulb text-[#165DFF]" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-white">
          优化建议
        </h3>
        <p class="text-xs text-[#909399]">
          提升输出的关键技巧
        </p>
      </div>
    </div>
    <div
      v-if="safeSuggestions.length > 0"
      class="space-y-3"
    >
      <div
        v-for="(suggestion, index) in safeSuggestions"
        :key="index"
        class="flex items-start gap-3 p-3 bg-[#2a2a2e] rounded-md"
      >
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
          :class="
            suggestion.priority === 'high' ? 'bg-red-500' :
            suggestion.priority === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
          "
        >
          {{ index + 1 }}
        </div>
        <div class="flex-1">
          <p class="text-white font-bold text-sm mb-1">
            {{ suggestion.title }}
          </p>
          <p class="text-xs text-[#909399]">
            {{ suggestion.description }}
          </p>
          <p class="text-xs text-green-400 mt-1">
            预估提升: {{ suggestion.expected_impact }}
          </p>
        </div>
      </div>
    </div>
    <div
      v-else
      class="text-[#909399] text-center py-8"
    >
      暂无优化建议
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
