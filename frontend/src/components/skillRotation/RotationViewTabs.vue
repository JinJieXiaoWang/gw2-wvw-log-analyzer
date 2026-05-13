<script setup lang="ts">
// 模块功能：技能循环视图切换组件
// 作者：帅姐姐
// 创建日期：2026-05-14

import type { ViewMode } from '@/models/skillRotation';

interface Props {
  modelValue: ViewMode
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: ViewMode]
}>()

const viewTabs: { id: ViewMode; label: string }[] = [
  { id: 'cycle', label: '循环视图' },
  { id: 'timeline', label: '时间轴' },
  { id: 'heatmap', label: '热力图' }
]

function selectView(view: ViewMode) {
  emit('update:modelValue', view)
}
</script>

<template>
  <div class="view-tabs flex gap-2 bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-1">
    <button
      v-for="tab in viewTabs"
      :key="tab.id"
      class="tab-button"
      :class="
        modelValue === tab.id
          ? 'tab-active bg-[#165DFF] text-white'
          : 'tab-inactive text-[#909399] hover:text-white hover:bg-[#2a2a2e]'
      "
      @click="selectView(tab.id)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped lang="postcss">
.tab-button {
  @apply px-4 py-2 rounded-md text-sm font-medium transition-all duration-200;
}
</style>
