<template>
  <div class="page-header-banner animate-slide-in-up">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
      <div class="flex items-center gap-4">
        <div
          class="w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg float-element"
          :class="iconGradient"
        >
          <i :class="[icon, 'text-3xl text-white']" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-neutral-text mb-1">
            {{ title }}
          </h1>
          <p class="text-neutral-text-secondary text-sm">
            {{ subtitle }}
          </p>
        </div>
      </div>
      <div class="flex gap-3 items-center">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * PageHeader - 通用页面头部组件
 * 功能：统一各模块页面标题区的视觉风格，通过 props 配置图标/标题，通过 slot 自定义右侧操作区
 * 作者：帅姐姐
 * 更新日期：2026-04-30
 */

interface Props {
  /** 图标类名，如 'pi pi-chart-bar' */
  icon: string
  /** 图标背景渐变类，如 'bg-gradient-to-br from-secondary to-primary' */
  iconGradient: string
  /** 页面标题 */
  title: string
  /** 页面副标题 */
  subtitle: string
}

defineProps<Props>()
</script>
