<template>
  <!-- 动态值，无法使用 Tailwind 静态类 -->
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex flex-col lg:flex-row gap-4 items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">日期范围筛选</label>
        <Calendar
          v-model="localDateRange"
          selection-mode="range"
          date-format="yy-mm-dd"
          placeholder="选择日期范围"
          show-icon
          class="w-full"
        />
      </div>
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">搜索角色名称</label>
        <BaseInput
          v-model="localSearch"
          placeholder="输入角色名称"
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-40">
        <label class="block text-sm text-neutral-text-secondary mb-2">地图筛选</label>
        <BaseSelect
          v-model="localMap"
          :options="filterOptions.maps"
          placeholder="选择地图"
          show-clear
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-40">
        <label class="block text-sm text-neutral-text-secondary mb-2">职业筛选</label>
        <BaseSelect
          v-model="localProfession"
          :options="filterOptions.professions"
          placeholder="选择职业"
          show-clear
          class="w-full"
        />
      </div>
      <BaseButton
        label="筛选"
        icon="pi pi-search"
        class="btn-game"
        :loading="loading"
        @click="$emit('apply')"
      />
      <BaseButton
        label="重置"
        icon="pi pi-refresh"
        class="btn-ghost"
        :disabled="loading"
        @click="$emit('reset')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Calendar from 'primevue/calendar'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

/** 筛选条件值 */
interface FilterValues {
  /** 日期范围 */
  dateRange: Date[] | null
  /** 搜索关键词 */
  searchQuery: string
  /** 地图筛选 */
  filterMap: string | null
  /** 职业筛选 */
  filterProfession: string | null
}

const props = defineProps<{
  filterValues: FilterValues
  filterOptions: { maps: string[]; professions: string[] }
  loading: boolean
}>()

const emit = defineEmits<{
  'update:filterValues': [value: FilterValues]
  apply: []
  reset: []
}>()

const localDateRange = computed({
  get: () => props.filterValues.dateRange,
  set: v => emit('update:filterValues', { ...props.filterValues, dateRange: v })
})
const localSearch = computed({
  get: () => props.filterValues.searchQuery,
  set: v => emit('update:filterValues', { ...props.filterValues, searchQuery: v })
})
const localMap = computed({
  get: () => props.filterValues.filterMap,
  set: v => emit('update:filterValues', { ...props.filterValues, filterMap: v })
})
const localProfession = computed({
  get: () => props.filterValues.filterProfession,
  set: v => emit('update:filterValues', { ...props.filterValues, filterProfession: v })
})
</script>
