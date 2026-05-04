<template>
  <div class="dict-select">
    <Select
      v-model="innerValue"
      :options="currentOptions as any[]"
      :option-label="optionLabel"
      :option-value="optionValue"
      :placeholder="placeholder"
      :disabled="disabled || loading"
      :filter="filter"
      :show-clear="showClear"
      :loading="loading || dictLoading"
      class="w-full"
      @change="handleChange"
    >
      <template #value="slotProps">
        <div
          v-if="slotProps.value"
          class="flex items-center gap-2"
        >
          <span
            v-if="showColor && getOptionColor(slotProps.value)"
            class="w-3 h-3 rounded-full flex-shrink-0"
            :style="{ backgroundColor: getOptionColor(slotProps.value) }"
          />
          <span>{{ getOptionLabel(slotProps.value) }}</span>
          <span
            v-if="showValue"
            class="text-neutral-text-tertiary text-xs"
          >({{ slotProps.value }})</span>
        </div>
        <span
          v-else
          class="text-neutral-text-disabled"
        >{{ placeholder }}</span>
      </template>

      <template #option="slotProps">
        <div class="flex items-center gap-2 py-0.5">
          <span
            v-if="showColor && slotProps.option.css_class"
            class="w-3 h-3 rounded-full flex-shrink-0"
            :style="{ backgroundColor: slotProps.option.css_class }"
          />
          <span>{{ slotProps.option[optionLabel] }}</span>
          <span
            v-if="showValue"
            class="text-neutral-text-tertiary text-xs"
          >({{ slotProps.option[optionValue] }})</span>
        </div>
      </template>

      <template #empty>
        <div class="py-2 text-center text-neutral-text-secondary text-sm">
          暂无选项
        </div>
      </template>
    </Select>
  </div>
</template>

<script setup lang="ts">
/**
 * DictSelect - 字典下拉选择组件
 * 功能：支持从字典类型自动加载选项，支持颜色预览、搜索等功能
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import { ref, watch, onMounted, computed } from 'vue'
import Select from 'primevue/select'
import { dictionaryService, type DictOption } from '@/services/system/dictionaryService'

interface SelectOption {
  label: string
  value: string
  css_class?: string
}

interface Props {
  /** 绑定值 */
  modelValue: string | number | null | undefined
  /** 字典类型编码（如 'profession', 'role'） */
  dictType?: string
  /** 自定义选项列表（可选，提供时优先使用） */
  options?: DictOption[] | null
  /** 标签字段名 */
  optionLabel?: string
  /** 值字段名 */
  optionValue?: string
  /** 占位提示 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否启用搜索 */
  filter?: boolean
  /** 是否显示清除按钮 */
  showClear?: boolean
  /** 是否显示值 */
  showValue?: boolean
  /** 加载状态 */
  loading?: boolean
  /** 是否显示颜色标记 */
  showColor?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  dictType: '',
  options: null,
  optionLabel: 'label',
  optionValue: 'value',
  placeholder: '请选择',
  disabled: false,
  filter: false,
  showClear: true,
  showValue: false,
  loading: false,
  showColor: true
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | null]
  change: [event: { value: any; originalEvent: Event }]
}>()

/** 字典选项缓存 */
const dictOptions = ref<DictOption[]>([])
/** 字典加载状态 */
const dictLoading = ref(false)

/**
 * 当前使用的选项列表
 */
const currentOptions = computed<SelectOption[]>(() => {
  if (props.options && props.options.length > 0) {
    return props.options.map(o => ({
      label: o.label || '',
      value: o.value || '',
      css_class: o.css_class
    }))
  }
  return dictOptions.value.map(o => ({
    label: o.label || '',
    value: o.value || '',
    css_class: o.css_class
  }))
})

/**
 * 内部绑定值（用于 v-model）
 */
const innerValue = computed({
  get: () => props.modelValue as any,
  set: (val: any) => {
    emit('update:modelValue', val)
  }
})

/**
 * 加载字典选项
 */
async function loadDictOptions() {
  if (!props.dictType || (props.options && props.options.length > 0)) {
    return
  }

  dictLoading.value = true
  try {
    const result = await dictionaryService.getOptions(props.dictType)
    dictOptions.value = result
  } catch (error) {
    console.error(`[DictSelect] 加载字典选项失败: ${props.dictType}`, error)
    dictOptions.value = []
  } finally {
    dictLoading.value = false
  }
}

/**
 * 获取选项标签
 */
function getOptionLabel(value: string | number): string {
  const opt = currentOptions.value.find(o => o[props.optionValue as keyof DictOption] === String(value))
  return opt ? (opt[props.optionLabel as keyof DictOption] as string) : String(value)
}

/**
 * 获取选项颜色
 */
function getOptionColor(value: string | number): string | undefined {
  const opt = currentOptions.value.find(o => o[props.optionValue as keyof DictOption] === String(value))
  return opt?.css_class
}

/**
 * 处理选择变更
 */
function handleChange(event: { value: any; originalEvent: Event }) {
  emit('change', event)
}

// 监听字典类型变化
watch(() => props.dictType, (newType, oldType) => {
  if (newType && newType !== oldType) {
    loadDictOptions()
  }
})

// 组件挂载时加载
onMounted(() => {
  loadDictOptions()
})
</script>

<style scoped>
.dict-select :deep(.p-select) {
  width: 100%;
}
</style>
