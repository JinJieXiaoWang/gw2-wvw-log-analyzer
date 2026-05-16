<template>
  <!-- 动态值，无法使用 Tailwind 静态类 -->
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.1s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
        <i class="pi pi-filter text-primary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          筛选条件
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          精确查找所需的数据
        </p>
      </div>
    </div>
    <div class="flex flex-col lg:flex-row gap-4 items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">日期范围</label>
        <Calendar
          v-model="localDateRange"
          selection-mode="range"
          date-format="yy-mm-dd"
          placeholder="选择日期范围"
          show-icon
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-48">
        <label class="block text-sm text-neutral-text-secondary mb-2">服务器</label>
        <Dropdown
          v-model="localFilters.serverName"
          :options="serverOptions"
          option-label="label"
          option-value="value"
          placeholder="选择服务器"
          show-clear
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-48">
        <label class="block text-sm text-neutral-text-secondary mb-2">地图</label>
        <Dropdown
          v-model="localFilters.mapName"
          :options="mapOptions"
          option-label="label"
          option-value="value"
          placeholder="选择地图"
          show-clear
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-48">
        <label class="block text-sm text-neutral-text-secondary mb-2">职业</label>
        <Dropdown
          v-model="localFilters.profession"
          :options="professionOptions"
          option-label="label"
          option-value="value"
          placeholder="选择职业"
          show-clear
          class="w-full"
        />
      </div>
      <BaseButton
        label="应用筛选"
        icon="pi pi-search"
        variant="game"
        @click="applyFilters"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤统计筛选组件
 * 功能：提供日期范围、服务器、地图和职业的筛选功能
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, watch, reactive } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'

// v-model
const dateRange = defineModel<Date[] | null>('dateRange', { default: null })
const filters = defineModel<{
  serverName: string | null
  mapName: string | null
  profession: string | null
}>('filters', { default: () => ({ serverName: null, mapName: null, profession: null }) })

// Props
const props = defineProps<{
  serverOptions: Array<{ label: string; value: string }>
  mapOptions: Array<{ label: string; value: string }>
  professionOptions: Array<{ label: string; value: string }>
}>()

// Emits
const emit = defineEmits<{
  'apply-filters': []
}>()

// 本地状态
const localDateRange = ref<Date[] | null>(dateRange.value)
const localFilters = reactive({
  serverName: filters.value.serverName,
  mapName: filters.value.mapName,
  profession: filters.value.profession
})

// 监听model变化
watch(() => dateRange.value, (newValue) => {
  localDateRange.value = newValue
})

watch(() => filters.value, (newValue) => {
  localFilters.serverName = newValue.serverName
  localFilters.mapName = newValue.mapName
  localFilters.profession = newValue.profession
}, { deep: true })

// 监听本地状态变化
watch(localDateRange, (newValue) => {
  dateRange.value = newValue
})

watch(localFilters, (newValue) => {
  filters.value = { ...newValue }
}, { deep: true })

// 事件处理
const applyFilters = () => {
  emit('apply-filters')
}
</script>