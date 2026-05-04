<template>
  <span
    class="dict-value"
    :style="displayStyle"
    :class="{ 'dict-value-not-found': !mappingResult.found }"
  >
    {{ mappingResult.label }}
  </span>
</template>

<script setup lang="ts">
import { computed, watch, onMounted } from 'vue'
import { getDictMapping, loadDictMapping, type DictMappingResult } from '@/utils/profession/dictMapping'

/**
 * 字典值显示组件
 * 功能：根据字典类型和值，显示对应的标签和颜色
 * 支持职业(profession/occupation)和精英特长(specialization/elite_specialty)
 */

const props = defineProps<{
  /** 字典类型 */
  dictType: string
  /** 字典值 */
  value: string | null | undefined
  /** 默认显示值 */
  defaultValue?: string
  /** 默认颜色 */
  defaultColor?: string
  /** 是否加粗显示 */
  bold?: boolean
  /** 是否添加边框 */
  bordered?: boolean
}>()

const emit = defineEmits<{
  /** 映射完成事件 */
  (e: 'mapped', result: DictMappingResult): void
}>()

const mappingResult = computed<DictMappingResult>(() => {
  return getDictMapping(props.dictType, props.value)
})

const displayStyle = computed(() => {
  const styles: Record<string, string> = {
    color: mappingResult.value.color,
  }
  
  if (props.bold) {
    styles.fontWeight = 'bold'
  }
  
  if (props.bordered) {
    styles.border = `1px solid ${mappingResult.value.color}`
    styles.borderRadius = '4px'
    styles.padding = '2px 8px'
  }
  
  return styles
})

/**
 * 异步加载最新的字典数据
 */
const loadMapping = async () => {
  try {
    await loadDictMapping(props.dictType)
    emit('mapped', mappingResult.value)
  } catch (error) {
    console.error('[DictValue] 加载字典映射失败', error)
  }
}

onMounted(() => {
  loadMapping()
})

watch(() => [props.dictType, props.value], () => {
  loadMapping()
})
</script>

<style scoped>
.dict-value {
  display: inline-block;
  transition: color 0.2s ease;
}

.dict-value-not-found {
  opacity: 0.6;
  font-style: italic;
}
</style>
