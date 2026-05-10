<!-- TODO[PrimeVue]: 可使用 PrimeVue ProgressSpinner 或 Skeleton 组件替代 -->
<template>
  <div
    class="flex flex-col items-center justify-center py-10 px-4 gap-4"
    role="status"
    aria-busy="true"
    :aria-label="ariaLabel"
    v-bind="$attrs"
  >
    <div
      class="text-primary"
      :class="{ 'text-ai': variant === 'ai' }"
    >
      <i
        class="pi pi-spin pi-spinner"
        aria-hidden="true"
        :style="{ fontSize: `${size}px` }"
      />
    </div>
    <p
      v-if="text"
      class="text-neutral-text-secondary text-sm m-0"
    >
      {{ text }}
    </p>
  </div>
</template>

<script setup lang="ts">
/**
 * 加载状态组件
 * 功能：展示数据加载中的状态
 * 支持普通加载和 AI 分析加载两种变体
 * 作者：˧姐姐
 * 创建时间：2026-04-27
 * 更新时间：2026-05-10 - 增强无障碍支持，新增 AI 变体
 */

import { computed } from 'vue'

interface Props {
  text?: string
  size?: number
  /** 加载变体：default（普通加载）、ai（ AI 分析加载） */
  variant?: 'default' | 'ai'
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  size: 32,
  variant: 'default'
})

const ariaLabel = computed(() => {
  if (props.text) return props.text
  return props.variant === 'ai' ? 'AI 分析加载中' : '加载中'
})
</script>
