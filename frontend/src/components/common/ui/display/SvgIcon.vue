<template>
  <svg
    class="svg-icon inline-flex items-center justify-center shrink-0 hover:opacity-80"
    :class="svgClasses"
    :style="svgStyle"
    :width="width || iconSize"
    :height="height || iconSize"
    viewBox="0 0 24 24"
    fill="currentColor"
    :aria-hidden="true"
    :aria-label="title"
  >
    <title v-if="title">{{ title }}</title>
    <use :xlink:href="iconHref" />
  </svg>
</template>

<script setup lang="ts">
/**
 * SvgIcon 组件
 * 功能：统一的SVG图标组件，支持自定义尺寸、颜色、旋转和动画
 * 作者：System
 * 创建日期：2026-05-11
 * 
 * Props:
 * - name: 图标名称（必填）
 * - category: 图标分类（默认 'ui'）
 * - size: 图标尺寸（'xs' | 'sm' | 'md' | 'lg' | 'xl'）
 * - width/height: 自定义宽高
 * - color: 自定义颜色
 * - spin: 是否旋转动画
 * - inline: 是否内联显示
 * - title: 无障碍标签
 * - customClass: 自定义CSS类名
 * 
 * 使用示例：
 * <SvgIcon name="home" />
 * <SvgIcon name="log" category="ui" size="lg" color="var(--primary)" />
 */

import { computed } from 'vue'

interface Props {
  /** 图标名称 */
  name: string
  /** 图标分类：ui, combat, status, profession, buff, decor */
  category?: 'ui' | 'combat' | 'status' | 'profession' | 'buff' | 'decor'
  /** 图标尺寸 */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  /** 自定义宽度 */
  width?: number | string
  /** 自定义高度 */
  height?: number | string
  /** 自定义颜色 */
  color?: string
  /** 是否旋转动画 */
  spin?: boolean
  /** 是否内联显示 */
  inline?: boolean
  /** 无障碍标签 */
  title?: string
  /** 自定义CSS类名 */
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  category: 'ui',
  size: 'md',
  spin: false,
  inline: false
})

/**
 * 尺寸映射表
 */
const sizeMap: Record<string, number> = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32
}

/**
 * 计算图标大小
 */
const iconSize = computed(() => sizeMap[props.size] || sizeMap.md)

/**
 * 计算图标href
 */
const iconHref = computed(() => {
  return `#icon-${props.category}-${props.name}`
})

/**
 * 计算SVG类名
 */
const svgClasses = computed(() => {
  const classes: string[] = [`svg-icon--${props.size}`]
  
  if (props.spin) {
    classes.push('svg-icon--spin')
  }
  if (props.inline) {
    classes.push('svg-icon--inline')
  }
  if (props.customClass) {
    classes.push(props.customClass)
  }
  
  return classes
})

/**
 * 计算SVG样式
 */
const svgStyle = computed(() => {
  const style: Record<string, string> = {}
  if (props.color) {
    style.color = props.color
  }
  return style
})
</script>

<style scoped>
.svg-icon--spin {
  animation: svg-spin 2s linear infinite;
}
@keyframes svg-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.svg-icon:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  border-radius: 2px;
}
</style>
