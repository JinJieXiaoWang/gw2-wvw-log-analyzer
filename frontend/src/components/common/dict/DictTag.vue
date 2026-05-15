<script setup lang="ts">
/**
 * DictTag - 字典标签组件
 * 功能：自动将字典值翻译为标签文本，根据字典 css_class 显示颜色
 * 使用方式替代直接写死的三元判断：data.status === 0 ? '启用' : '禁用'
 *
 * 示例：
 *   <DictTag dict-type="sys_normal_disable" :value="data.status" />
 *   <DictTag dict-type="role" :value="data.role_type" variant="badge" />
 *   <DictTag dict-type="parse_status" :value="log.status" variant="text" show-dot />
 */

import { computed } from 'vue'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import { useDictStore } from '@/store/system/dict'

interface Props {
  /** 字典类型编码 */
  dictType: string
  /** 字典值 */
  value?: string | number | null
  /** 显示变体 */
  variant?: 'tag' | 'badge' | 'text'
  /** 是否显示颜色圆点（仅 text 模式有效） */
  showDot?: boolean
  /** 找不到字典项时的占位文本 */
  placeholder?: string
  /** 自定义 severity，优先级低于字典 css_class */
  severity?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'tag',
  showDot: false,
  placeholder: '-',
})

const dictStore = useDictStore()

/** 通用状态 fallback 映射（当字典未加载时兜底） */
const FALLBACK_LABELS: Record<string, Record<string, string>> = {
  sys_normal_disable: { '0': '启用', '1': '禁用' },
  parse_status: {
    pending: '待解析',
    parsing: '解析中',
    completed: '已完成',
    failed: '失败',
    retrying: '重试中',
    partial: '部分完成',
  },
  role: {
    dps: '输出',
    support: '辅助',
    tank: '承伤',
    condition: '症状',
    healing: '治疗',
    control: '控制',
    utility: '功能',
  },
}

/** 显示标签 */
const displayLabel = computed(() => {
  if (props.value === undefined || props.value === null || props.value === '') {
    return props.placeholder
  }
  const label = dictStore.getDictLabel(props.dictType, props.value)
  // 如果字典返回原值（未找到或字典未加载），尝试 fallback
  if (label === String(props.value)) {
    const fallback = FALLBACK_LABELS[props.dictType]?.[String(props.value)]
    if (fallback) return fallback
  }
  return label
})

/** 字典项颜色 */
const dictColor = computed(() => {
  if (props.value === undefined || props.value === null) return ''
  return dictStore.getDictColor(props.dictType, props.value)
})

/** 是否是 Hex 颜色 */
const isHexColor = computed(() => {
  return dictColor.value && /^#[0-9A-Fa-f]{6}$/.test(dictColor.value)
})

/** 推断 severity：优先用字典 css_class，其次 props.severity，最后按值推断 */
const computedSeverity = computed(() => {
  const css = dictColor.value
  // 如果 css_class 是 PrimeVue 支持的 severity 名称
  const validSeverities = ['success', 'info', 'warning', 'danger', 'secondary', 'contrast']
  if (css && validSeverities.includes(css)) {
    return css
  }
  // 使用传入的 severity
  if (props.severity) {
    return props.severity
  }
  // 按常用值推断（兜底）
  const val = String(props.value).toLowerCase()
  if (val === '0' || val === 'completed' || val === 'success' || val === 'enabled') return 'success'
  if (val === '1' || val === 'failed' || val === 'error' || val === 'disabled') return 'danger'
  if (val === 'pending' || val === 'warning') return 'warning'
  if (val === 'parsing' || val === 'processing') return 'info'
  return 'secondary'
})

/** 自定义样式（Hex 颜色时直接设置背景） */
const customStyle = computed(() => {
  if (isHexColor.value && props.variant !== 'text') {
    return {
      backgroundColor: dictColor.value,
      color: '#fff',
    }
  }
  return {}
})
</script>

<template>
  <!-- Tag 变体 -->
  <Tag
    v-if="variant === 'tag'"
    v-bind="$attrs"
    :value="displayLabel"
    :severity="computedSeverity"
    :style="customStyle"
  />

  <!-- Badge 变体 -->
  <Badge
    v-else-if="variant === 'badge'"
    v-bind="$attrs"
    :value="displayLabel"
    :severity="computedSeverity"
    :style="customStyle"
  />

  <!-- Text 变体（纯文本 + 可选颜色圆点） -->
  <span
    v-else
    v-bind="$attrs"
    class="dict-tag-text"
  >
    <span
      v-if="showDot"
      class="dict-dot"
      :style="{ background: isHexColor ? dictColor : undefined }"
      :class="{ 'dict-dot--severity': !isHexColor }"
    />
    {{ displayLabel }}
  </span>
</template>

<style scoped>
.dict-tag-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text);
}

.dict-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.dict-dot--severity {
  background: var(--color-text-tertiary);
}
</style>
