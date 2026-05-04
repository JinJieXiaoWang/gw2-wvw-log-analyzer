<template>
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
      <Button
        label="应用筛选"
        icon="pi pi-search"
        class="btn-game"
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
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'

// Props
const props = defineProps<{
  dateRange: Date[] | null
  filters: {
    serverName: string | null
    mapName: string | null
    profession: string | null
  }
  serverOptions: Array<{ label: string; value: string }>
  mapOptions: Array<{ label: string; value: string }>
  professionOptions: Array<{ label: string; value: string }>
}>()

// Emits
const emit = defineEmits<{
  'update:dateRange': [value: Date[] | null]
  'update:filters': [value: { serverName: string | null; mapName: string | null; profession: string | null }]
  'apply-filters': []
}>()

// 本地状态
const localDateRange = ref<Date[] | null>(props.dateRange)
const localFilters = reactive({
  serverName: props.filters.serverName,
  mapName: props.filters.mapName,
  profession: props.filters.profession
})

// 监听props变化
watch(() => props.dateRange, (newValue) => {
  localDateRange.value = newValue
})

watch(() => props.filters, (newValue) => {
  localFilters.serverName = newValue.serverName
  localFilters.mapName = newValue.mapName
  localFilters.profession = newValue.profession
}, { deep: true })

// 监听本地状态变化
watch(localDateRange, (newValue) => {
  emit('update:dateRange', newValue)
})

watch(localFilters, (newValue) => {
  emit('update:filters', { ...newValue })
}, { deep: true })

// 事件处理
const applyFilters = () => {
  emit('apply-filters')
}
</script>