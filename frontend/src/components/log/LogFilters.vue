<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex flex-col lg:flex-row gap-4 items-center">
      <div class="flex-1 w-full">
        <InputText
          v-model="localFilters.search"
          placeholder="搜索日志"
          class="w-full"
        />
      </div>
      <div class="flex flex-wrap gap-3 items-center">
        <DictSelect
          v-model="localFilters.status"
          dict-type="parse_status"
          placeholder="选择状态"
          show-clear
          class="w-40"
        />
        <BaseButton
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
 * 功能：处理日志筛选
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */
import { ref, computed, watch } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import DictSelect from '@/components/common/dict/DictSelect.vue'
import InputText from 'primevue/inputtext'
import { debounce } from '@/utils/core/helpers'
import { useDictStore } from '@/store/system/dict'

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

// 本地状漼?
const localFilters = ref({ ...props.filters })

const dictStore = useDictStore()
// 预加载解析状态字典
dictStore.loadDict('parse_status')

// 计算属性
const hasActiveFilters = computed(() => {
  return localFilters.value.search || localFilters.value.status
})

// 防抖发射筛选值
const emitDebounced = debounce((value: typeof localFilters.value) => {
  emit('update:filters', { ...value })
}, 300)

// 监听本地筛选值变化
watch(localFilters, (newValue) => {
  emitDebounced(newValue)
}, { deep: true })

// 清除筛选值
const clearFilters = () => {
  localFilters.value = {
    search: '',
    status: null
  }
  emit('update:filters', { ...localFilters.value })
}
</script>