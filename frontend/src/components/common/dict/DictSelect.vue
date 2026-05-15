<script setup lang="ts">
/**
 * DictSelect - 字典下拉选择组件
 * 功能：自动从字典加载选项，支持颜色预览
 * 替代手动定义选项数组的场景
 *
 * 示例：
 *   <DictSelect v-model="form.status" dict-type="sys_normal_disable" placeholder="选择状态" />
 *   <DictSelect v-model="form.role" dict-type="role" show-color />
 */

import { computed, watch } from 'vue'
import Select from 'primevue/select'
import { useDictStore } from '@/store/system/dict'

interface Props {
  /** 字典类型编码 */
  dictType: string
  /** 占位文本 */
  placeholder?: string
  /** 是否显示颜色预览 */
  showColor?: boolean
  /** 是否显示清除按钮 */
  showClear?: boolean
  /** 是否禁用 */
  disabled?: boolean
  /** 是否过滤 */
  filter?: boolean
  /** 尺寸 */
  size?: 'small' | 'normal' | 'large'
  /** 是否多选 */
  multiple?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择',
  showColor: false,
  showClear: false,
  disabled: false,
  filter: false,
  size: 'normal',
  multiple: false,
})

const modelValue = defineModel<string | number | string[] | number[] | null>()

const dictStore = useDictStore()

/** 字典选项 */
const options = computed(() => {
  const dictData = dictStore.getDict(props.dictType)
  if (!dictData) return []
  return dictData.map((item) => ({
    label: item.label,
    value: item.value,
    color: item.css_class || '',
  }))
})

/** 自动加载字典 */
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

<template>
  <Select
    v-model="modelValue"
    :options="options"
    option-label="label"
    option-value="value"
    :placeholder="placeholder"
    :show-clear="showClear"
    :disabled="disabled"
    :filter="filter"
    :size="size"
    :multiple="multiple"
    v-bind="$attrs"
  >
    <!-- 选项模板：带颜色预览 -->
    <template
      v-if="showColor"
      #option="slotProps"
    >
      <div class="dict-option">
        <span
          v-if="slotProps.option.color"
          class="dict-option-dot"
          :style="{ background: slotProps.option.color }"
        />
        <span class="dict-option-label">{{ slotProps.option.label }}</span>
      </div>
    </template>

    <!-- 值模板：带颜色预览 -->
    <template
      v-if="showColor"
      #value="slotProps"
    >
      <div
        v-if="slotProps.value"
        class="dict-option"
      >
        <span
          v-if="slotProps.value.color"
          class="dict-option-dot"
          :style="{ background: slotProps.value.color }"
        />
        <span class="dict-option-label">{{ slotProps.value.label }}</span>
      </div>
      <span v-else>{{ placeholder }}</span>
    </template>

    <!-- 透传其他插槽 -->
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
  </Select>
</template>

<style scoped>
.dict-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dict-option-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dict-option-label {
  color: var(--color-text);
}
</style>
