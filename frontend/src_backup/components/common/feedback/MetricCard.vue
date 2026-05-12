<template>
  <div
    class="animate-slide-in-up"
    :class="cardClass"
    :style="{ animationDelay: `${animationDelay}s` }"
  >
    <div class="flex items-center justify-between">
      <div class="min-w-0 flex-1">
        <p class="text-neutral-text-secondary text-sm mb-1">
          {{ label }}
        </p>
        <p
          class="text-3xl font-bold truncate"
          :class="valueClass"
        >
          {{ value }}
        </p>
        <div class="flex items-center gap-1 mt-2">
          <slot name="extra" />
        </div>
      </div>
      <div
        class="rounded-xl flex items-center justify-center flex-shrink-0 ml-3"
        :class="[iconSizeClass, iconBgClass]"
      >
        <i :class="[icon, iconColor, iconTextClass]" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MetricCard - ָ标卡片组件
 * 功能：统一各模块统计卡片的视觉风格，支持游戏风格稀有度样式
 * 作者：˧姐姐
 * 更新日期：2026-04-30
 */

interface Props {
  /** ָ标标签 */
  label: string
  /** ָ标值 */
  value: string | number
  /** 图标类名 */
  icon: string
  /** 图标颜色类 */
  iconColor: string
  /** 卡片稀有度样式：card-legendary | card-exotic | card-rare */
  cardClass: string
  /** 数值颜色类 */
  valueClass?: string
  /** 图标背景样式类 */
  iconBgClass?: string
  /** 图标容器尺寸 */
  iconSizeClass?: string
  /** 图标文字尺寸 */
  iconTextClass?: string
  /** 动画延迟（秒） */
  animationDelay?: number
}

withDefaults(defineProps<Props>(), {
  valueClass: 'game-number',
  iconBgClass: 'bg-gradient-to-br from-primary/30 to-secondary/30',
  iconSizeClass: 'w-12 h-12',
  iconTextClass: 'text-xl',
  animationDelay: 0
})
</script>
