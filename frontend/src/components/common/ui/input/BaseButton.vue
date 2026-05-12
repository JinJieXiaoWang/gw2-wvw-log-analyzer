<script setup lang="ts">
/**
 * BaseButton - 游戏化风格按钮封装
 *
 * 设计理念：
 * 1. 拥抱 PrimeVue v4 PT (Pass Through) 机制，不再手动拼接 CSS 类名。
 * 2. 统一 API，使用 severity 控制语义颜色，使用 standard props 控制形态。
 * 3. 支持 Tailwind CSS 原子类透传。
 * 4. 兼容旧版 variant API（primary/secondary/game/ghost/ai/outline/danger/success），
 *    在内部自动映射为 PrimeVue v4 标准 severity + variant。
 *
 * 使用示例：
 * <BaseButton label="主要按钮" severity="primary" />
 * <BaseButton label="危险操作" severity="danger" outlined />
 * <BaseButton icon="pi pi-check" severity="success" />
 * <BaseButton label="AI 模式" class="bg-gradient-to-r from-purple-500 to-indigo-500 border-0" />
 */

import type { ButtonProps } from 'primevue/button'
import Button from 'primevue/button'
import { computed } from 'vue'

// 扩展 PrimeVue 原生 Props，兼容旧版非标准 variant
interface Props extends /* @vue-ignore */ ButtonProps {
  customVariant?: 'game' | 'ai'
  icon?: string
  label?: string
  iconPos?: string
  loading?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  severity: 'secondary',
  variant: 'text',
  size: 'normal',
  loading: false,
  disabled: false,
  iconPos: 'left',
  customVariant: undefined,
  icon: undefined,
  label: undefined
})

/**
 * 不声明任何 emit，让父组件的所有事件监听器（如 @click）通过 $attrs 自然透传给
 * 内部 PrimeVue <Button>，确保功能调用无拦截。
 */

// =============================================================================
// 兼容层：将旧版 variant 映射为 PrimeVue v4 标准 severity / variant
// =============================================================================

const computedSeverity = computed(() => {
  const v = props.variant as string | undefined
  if (v === 'danger') return 'danger'
  if (v === 'success') return 'success'
  if (v === 'primary') return undefined
  if (v === 'secondary') return 'secondary'
  if (v === 'ghost' || v === 'outline') return 'secondary'
  if (v === 'game' || v === 'ai') return undefined
  return props.severity
})

const computedVariant = computed(() => {
  const v = props.variant as string | undefined
  if (v === 'text' || v === 'outlined' || v === 'link') return v
  if (v === 'ghost') return 'text'
  if (v === 'outline') return 'outlined'
  return props.variant
})

const computedSize = computed(() => {
  const s = props.size
  if (s === 'small' || s === 'large') return s
  return undefined
})

// =============================================================================
// PT 配置：完全通过 Pass Through 控制根节点样式
// =============================================================================

const ptConfig = {
  root: ({ props: btnProps }: { props: ButtonProps }) => ({
    class: [
      // 基础布局与字体
      'font-medium rounded-xl transition-duration-200 duration-200 uppercase tracking-wide',

      // 尺寸控制
      btnProps.size === 'small' ? 'text-xs py-2 px-3' : '',
      btnProps.size === 'large' ? 'text-lg py-3 px-4' : '',
      btnProps.size === 'normal' ? 'text-sm py-2 px-4' : '',

      // 自定义变体（兼容旧版 variant="game|ai" 以及新版 customVariant）
      (props.customVariant === 'game' || props.variant === 'game') ? 'game-btn-style' : '',
      (props.customVariant === 'ai' || props.variant === 'ai') ? 'ai-btn-style' : ''
    ]
  })
}
</script>

<template>
  <Button
    v-bind="$attrs"
    :severity="computedSeverity"
    :variant="computedVariant"
    :size="computedSize"
    :loading="loading"
    :disabled="disabled"
    :icon="icon"
    :icon-pos="iconPos"
    :label="label"
    :pt="ptConfig"
    class="base-button"
  >
    <!-- 透传所有插槽 -->
    <template
      v-for="(_, name) in $slots"
      :key="name"
      #[name]="slotData"
    >
      <slot
        :name="name"
        v-bind="slotData || {}"
      />
    </template>
  </Button>
</template>

<style scoped>
/*
  仅保留极其特殊的、无法通过 Tailwind 或 PT 实现的样式。
  大部分样式应通过 PT 或 Tailwind 在组件上直接控制。
*/

/* 自定义变体：游戏风格 */
:deep(.game-btn-style) {
  @apply border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black shadow-[0_0_10px_rgba(250,204,21,0.5)];
}

/* 自定义变体：AI 风格 */
:deep(.ai-btn-style) {
  @apply bg-gradient-to-r from-purple-600 to-indigo-600 border-0 text-white hover:opacity-90 shadow-lg;
}
</style>
