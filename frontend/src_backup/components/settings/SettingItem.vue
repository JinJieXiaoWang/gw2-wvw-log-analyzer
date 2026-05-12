<template>
  <div
    class="setting-item group flex items-center justify-between gap-4 p-4 bg-neutral-bg rounded-xl border border-neutral-border transition-all duration-200"
    :class="{
      'hover:border-neutral-border-light': !disabled,
      'opacity-60 cursor-not-allowed': disabled
    }"
  >
    <!-- 左侧内容 -->
    <div class="flex items-center gap-3 min-w-0">
      <!-- 图标 -->
      <div
        v-if="icon"
        class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors"
        :class="iconBgClass"
        :style="iconBgStyle"
      >
        <i
          :class="[icon, 'text-base', iconClass]"
          :style="iconStyle"
        />
      </div>
      <!-- 文字 -->
      <div class="min-w-0">
        <p class="text-sm font-medium text-neutral-text truncate">
          {{ title }}
        </p>
        <p
          v-if="description"
          class="text-xs text-neutral-text-secondary mt-0.5"
        >
          {{ description }}
        </p>
      </div>
    </div>

    <!-- 右侧操作区 -->
    <div class="flex items-center gap-2 flex-shrink-0">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SettingItem - 统一设置项组件
 * 功能：提供一致的设置项行样式，包含图标、标题、描述和右侧操作区
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import { computed } from 'vue'

interface Props {
  /** 标题 */
  title: string
  /** 描述 */
  description?: string
  /** 图标类名 */
  icon?: string
  /** 图标颜色（CSS颜色值或Tailwind颜色类） */
  iconColor?: string
  /** 是否禁用 */
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  description: '',
  icon: '',
  iconColor: 'primary',
  disabled: false
})

/**
 * 判断 iconColor 是否为 Tailwind 类名（不含 # 和 rgb）
 */
const isTailwindColor = computed(() => {
  return props.iconColor && !props.iconColor.startsWith('#') && !props.iconColor.startsWith('rgb')
})

const iconBgClass = computed(() => {
  if (!isTailwindColor.value) return ''
  const colorMap: Record<string, string> = {
    primary: 'bg-primary/10',
    secondary: 'bg-secondary/10',
    success: 'bg-success/10',
    warning: 'bg-warning/10',
    error: 'bg-error/10',
    info: 'bg-info/10',
    ai: 'bg-ai/10'
  }
  return colorMap[props.iconColor] || 'bg-primary/10'
})

const iconBgStyle = computed(() => {
  if (isTailwindColor.value) return {}
  return { backgroundColor: props.iconColor + '15' }
})

const iconClass = computed(() => {
  if (!isTailwindColor.value) return ''
  const colorMap: Record<string, string> = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    success: 'text-success',
    warning: 'text-warning',
    error: 'text-error',
    info: 'text-info',
    ai: 'text-ai'
  }
  return colorMap[props.iconColor] || 'text-primary'
})

const iconStyle = computed(() => {
  if (isTailwindColor.value) return {}
  return { color: props.iconColor }
})
</script>

<style scoped>
.setting-item:hover {
  box-shadow: 0 0 20px var(--color-primary-alpha-5);
}
</style>
