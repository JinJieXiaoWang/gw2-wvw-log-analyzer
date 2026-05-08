<template>
  <span
    v-if="variant === 'text'"
    class="inline-flex items-center gap-1.5"
    :class="textClass"
    :style="textStyle"
  >
    <span
      v-if="showDot && color"
      class="w-2 h-2 rounded-full inline-block"
      :style="{ backgroundColor: color }"
    />
    <span>{{ displayLabel }}</span>
  </span>

  <Tag
    v-else-if="variant === 'tag'"
    :value="displayLabel"
    :severity="computedSeverity"
    :class="tagClass"
    :style="tagStyle"
  >
    <template v-if="$slots.default">
      <slot :label="displayLabel" :value="displayValue" :color="color" />
    </template>
  </Tag>

  <Badge
    v-else-if="variant === 'badge'"
    :value="displayLabel"
    :severity="computedSeverity"
    :class="badgeClass"
    :style="badgeStyle"
  />

  <span
    v-else
    class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium"
    :class="pillClass"
    :style="pillStyle"
  >
    <span
      v-if="showDot && color"
      class="w-1.5 h-1.5 rounded-full inline-block"
      :style="{ backgroundColor: color }"
    />
    <span>{{ displayLabel }}</span>
  </span>
</template>

<script setup lang="ts">
/**
 * DictTag - 字典标签组件
 * 功能：根据字典类型和值自动显示标签文本，支持颜色高亮
 * 设计理念：借鉴若依 DictTag，零配置自动翻译 + 颜色映射
 * 作者：系统
 * 创建日期：2026-05-07
 *
 * 使用示例：
 *   <DictTag dict-type="role" value="dps" />
 *   <DictTag dict-type="profession" value="Guardian" variant="badge" />
 *   <DictTag dict-type="role" value="support" variant="pill" show-dot />
 */

import { computed, watch } from 'vue'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import { useDictStore } from '@/store/system/dict'

interface Props {
  /** 字典类型编码 */
  dictType: string
  /** 字典值 */
  value?: string | number | null
  /** 显示变体：text-纯文本 / tag-PrimeVue Tag / badge-PrimeVue Badge / pill-圆角标签（默认） */
  variant?: 'text' | 'tag' | 'badge' | 'pill'
  /** 是否显示颜色圆点（仅 text/pill 有效） */
  showDot?: boolean
  /** 为空时的占位文本 */
  placeholder?: string
  /** 自定义 CSS 类 */
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'pill',
  showDot: true,
  placeholder: '-',
})

const dictStore = useDictStore()

/** 显示的标签文本 */
const displayLabel = computed(() => {
  if (props.value === undefined || props.value === null || props.value === '') {
    return props.placeholder
  }
  return dictStore.getDictLabel(props.dictType, props.value)
})

/** 原始值 */
const displayValue = computed(() => String(props.value ?? ''))

/** 字典项颜色 */
const color = computed(() => {
  if (props.value === undefined || props.value === null) return ''
  return dictStore.getDictColor(props.dictType, props.value)
})

/** 自动推断 PrimeVue severity */
const computedSeverity = computed(() => {
  // 如果字典有颜色，尝试映射到 PrimeVue severity
  const c = color.value.toLowerCase()
  if (c.includes('ff') && c.includes('4d')) return 'danger'      // 红
  if (c.includes('00') && c.includes('d6')) return 'success'     // 绿
  if (c.includes('35') && c.includes('b0')) return 'info'        // 蓝
  if (c.includes('ff') && c.includes('aa')) return 'warning'     // 橙
  if (c.includes('9d') && c.includes('4e')) return 'secondary'   // 紫
  return 'secondary'
})

/** pill 样式 */
const pillStyle = computed(() => {
  if (!color.value) return {}
  return {
    backgroundColor: color.value + '1A', // 10% 透明度
    color: color.value,
    border: `1px solid ${color.value}40`,
  }
})

const pillClass = computed(() => {
  return props.customClass || ''
})

/** text 样式 */
const textStyle = computed(() => {
  if (!color.value) return {}
  return { color: color.value }
})

const textClass = computed(() => {
  return `text-sm ${props.customClass || ''}`
})

/** tag 样式 */
const tagStyle = computed(() => {
  if (!color.value) return {}
  return {
    backgroundColor: color.value + '20',
    color: color.value,
    borderColor: color.value + '40',
  }
})

const tagClass = computed(() => {
  return `border ${props.customClass || ''}`
})

/** badge 样式（Badge 组件不支持自定义颜色，用 severity） */
const badgeStyle = computed(() => ({}))
const badgeClass = computed(() => props.customClass || '')

// 自动加载字典数据（如果缓存中没有）
watch(
  () => props.dictType,
  (type) => {
    if (type && !dictStore.hasDict(type)) {
      dictStore.loadDict(type)
    }
  },
  { immediate: true }
)
</script>
