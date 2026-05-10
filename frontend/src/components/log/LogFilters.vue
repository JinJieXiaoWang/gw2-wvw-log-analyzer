<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex flex-col lg:flex-row gap-4 items-center">
      <div class="flex-1 w-full">
        <InputText
          v-model="localFilters.search"
          placeholder="搜索文件鍚?.."
          class="w-full"
        />
      </div>
      <div class="flex flex-wrap gap-3 items-center">
        <BaseSelect
          v-model="localFilters.status"
          :options="statusOptions"
          option-label="label"
          option-value="value"
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
 * 日志绛涢技夌粍浠?
 * 功能锛氭彁渚涙棩蹇楁悳绱㈠拰绛涢技夊姛鑳?
 * 作輼咃細甯呭帅姐建日期锛?026-04-27
 */

import { ref, computed, watch } from 'vue'
import BaseButton from '@/components/common/ui/BaseButton.vue'
import BaseSelect from '@/components/common/ui/BaseSelect.vue'
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

// 本地状漼?
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

// 防抖发射筛鼼夊彉鍖栵紝閬垮厤棰戠箒杈撳叆瑙﹀彂閲嶆覆鏌?
const emitDebounced = debounce((value: typeof localFilters.value) => {
  emit('update:filters', { ...value })
}, 300)

// 监听本地筛鼼夋潯浠跺彉鍖?
watch(localFilters, (newValue) => {
  emitDebounced(newValue)
}, { deep: true })

// 娓呯┖筛鼼夋潯浠讹紙绔嬪嵆鐢熸晥锛屼笉璧伴槻鎶栵級
const clearFilters = () => {
  localFilters.value = {
    search: '',
    status: null
  }
  emit('update:filters', { ...localFilters.value })
}
</script>