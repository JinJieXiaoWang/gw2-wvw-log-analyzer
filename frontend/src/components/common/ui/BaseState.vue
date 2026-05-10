<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center gap-3" v-bind="$attrs">
    <div
      class="mb-2"
      :class="iconSizeClass"
      :style="{ color: iconColor }"
    >
      <i :class="icon" />
    </div>
    <h3 class="text-neutral-text text-lg font-semibold m-0">
      {{ title }}
    </h3>
    <p
      v-if="description"
      class="text-neutral-text-secondary text-sm max-w-xs m-0"
    >
      {{ description }}
    </p>
    <div class="flex items-center justify-center gap-3 mt-3 flex-wrap">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * BaseState - 状态提示基础封装组件
 * 功能：对PrimeVue State 的基础封装，用于项目中状态提示的视觉风格
 * 作者：帅姐姐 2026-04-30
 */

interface Props {
  /** 图标类名 */
  icon?: string
  /** 图标尺寸类 */
  iconSizeClass?: string
  /** 图标颜色（CSS 颜色值或 Tailwind 类） */
  iconColor?: string
  /** 标题 */
  title?: string
  /** 描述 */
  description?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'pi pi-inbox',
  iconSizeClass: 'text-6xl opacity-50',
  iconColor: '#909399',
  title: '',
  description: ''
})
</script>
