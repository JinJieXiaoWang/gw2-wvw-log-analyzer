<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex flex-col lg:flex-row gap-4 items-center">
      <div class="flex-1 w-full">
        <InputText
          v-model="localFilters.search"
          placeholder="搜索文件名..."
          class="w-full"
        />
      </div>
      <div class="flex flex-wrap gap-3 items-center">
        <Dropdown
          v-model="localFilters.status"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          placeholder="选择状态"
          show-clear
          class="w-40"
        />
        <Button
          v-if="hasActiveFilters"
          icon="pi pi-filter-slash"
          label="清除"
          class="btn-ghost whitespace-nowrap"
          @click="clearFilters"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 日志筛选组件
 * 功能：提供日志搜索和筛选功能
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, computed, watch } from 'vue'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import { debounce } from '@/utils/core/helpers'

// Props
const props = defineProps({
  filters: {
    type: Object,
    default: () => ({
      search: '',
      status: null
    })
  }
})

// Emits
const emit = defineEmits(['update:filters'])

// 本地状态
const localFilters = ref({ ...props.filters })

// 筛选选项配置
const statusOptions = [
  { label: '已完成', value: 'completed' },
  { label: '解析中', value: 'parsing' },
  { label: '待解析', value: 'pending' },
  { label: '失败', value: 'failed' }
]

// 计算属性
const hasActiveFilters = computed(() => {
  return localFilters.value.search || localFilters.value.status
})

// 防抖发射筛选变化，避免频繁输入触发重渲染
const emitDebounced = debounce((value: typeof localFilters.value) => {
  emit('update:filters', { ...value })
}, 300)

// 监听本地筛选条件变化
watch(localFilters, (newValue) => {
  emitDebounced(newValue)
}, { deep: true })

// 清空筛选条件（立即生效，不走防抖）
const clearFilters = () => {
  localFilters.value = {
    search: '',
    status: null
  }
  emit('update:filters', { ...localFilters.value })
}
</script>