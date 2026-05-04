<template>
  <div class="dict-tag inline-flex flex-wrap gap-1.5 items-center">
    <template v-if="displayTags.length > 0">
      <Tag
        v-for="(tag, index) in displayTags"
        :key="index"
        :value="tag.label"
        :severity="tag.severity"
        :style="tag.style"
        :class="tag.class"
        :rounded="true"
      />
    </template>
    <span
      v-else-if="showValue && rawValue"
      class="text-neutral-text-secondary text-sm"
    >
      {{ rawValue }}
    </span>
    <span
      v-else
      class="text-neutral-text-disabled text-sm"
    >
      -
    </span>
  </div>
</template>

<script setup lang="ts">
/**
 * DictTag - 字典标签组件
 * 功能：将字典值转换为标签显示，支持单值、多值、数组输入
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import { computed } from 'vue'
import Tag from 'primevue/tag'

interface DictOption {
  value: string
  label: string
  css_class?: string
  is_default?: number
  list_class?: string
}

interface Props {
  /** 字典选项列表 */
  options: DictOption[]
  /** 字典值（支持单值、逗号分隔多值、数组） */
  value: string | number | string[] | number[] | null | undefined
  /** 是否显示未匹配的值 */
  showValue?: boolean
  /** 多值分隔符 */
  separator?: string
}

const props = withDefaults(defineProps<Props>(), {
  showValue: true,
  separator: ','
})

/**
 * 解析输入值为字符串数组
 */
const parsedValues = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') {
    return []
  }

  if (Array.isArray(props.value)) {
    return props.value.map(v => String(v)).filter(v => v !== '')
  }

  return String(props.value)
    .split(props.separator)
    .map(v => v.trim())
    .filter(v => v !== '')
})

/**
 * 原始值字符串
 */
const rawValue = computed(() => {
  if (props.value === null || props.value === undefined) return ''
  return Array.isArray(props.value) ? props.value.join(props.separator) : String(props.value)
})

/**
 * 将 list_class 映射为 PrimeVue Tag severity
 */
function mapSeverity(listClass?: string): string | undefined {
  if (!listClass) return undefined
  const severityMap: Record<string, string> = {
    primary: 'info',
    secondary: 'secondary',
    success: 'success',
    danger: 'danger',
    warning: 'warn',
    info: 'info',
    contrast: 'contrast'
  }
  return severityMap[listClass] || undefined
}

/**
 * 生成显示标签列表
 */
const displayTags = computed(() => {
  return parsedValues.value.map(val => {
    const option = props.options.find(opt => opt.value === val)

    if (option) {
      const style: Record<string, string> = {}
      const cls: string[] = []

      if (option.css_class) {
        // 判断是否为颜色值（以 # 开头）
        if (option.css_class.startsWith('#')) {
          style.backgroundColor = option.css_class
          style.color = getContrastColor(option.css_class)
          style.borderColor = option.css_class
        } else {
          cls.push(option.css_class)
        }
      }

      return {
        label: option.label,
        severity: mapSeverity(option.list_class),
        style,
        class: cls.join(' ')
      }
    }

    // 未匹配的值
    return {
      label: val,
      severity: undefined as string | undefined,
      style: {} as Record<string, string>,
      class: 'bg-neutral-bg-secondary text-neutral-text-secondary border border-neutral-border'
    }
  })
})

/**
 * 根据背景色计算对比文字颜色（简单版本）
 */
function getContrastColor(hexColor: string): string {
  const hex = hexColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  const brightness = (r * 299 + g * 587 + b * 114) / 1000
  return brightness > 128 ? '#0D0D0F' : '#F0F0F5'
}
</script>

<style scoped>
.dict-tag :deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  font-weight: 500;
}
</style>
