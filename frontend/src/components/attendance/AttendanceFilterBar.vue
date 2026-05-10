<template>
  <div class="card animate-slide-in-up" style="animation-delay: 0.5s">
    <div class="flex flex-col lg:flex-row gap-4 items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">日期范围筛选</label>
        <Calendar v-model="localDateRange" selection-mode="range" date-format="yy-mm-dd" placeholder="选择日期范围" show-icon class="w-full" />
      </div>
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">搜索角色名称</label>
        <InputText v-model="localSearch" placeholder="输入角色名称" class="w-full" />
      </div>
      <div class="w-full lg:w-40">
        <label class="block text-sm text-neutral-text-secondary mb-2">地图筛选</label>
        <BaseSelect v-model="localMap" :options="filterOptions.maps" placeholder="选择地图" show-clear class="w-full" />
      </div>
      <div class="w-full lg:w-40">
        <label class="block text-sm text-neutral-text-secondary mb-2">职业筛选</label>
        <BaseSelect v-model="localProfession" :options="filterOptions.professions" placeholder="选择职业" show-clear class="w-full" />
      </div>
      <BaseButton label="筛选" icon="pi pi-search" class="btn-game" :loading="loading" @click="$emit('apply')" />
      <BaseButton label="重置" icon="pi pi-refresh" class="btn-ghost" :disabled="loading" @click="$emit('reset')" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Calendar from 'primevue/calendar'
import BaseSelect from '@/components/common/ui/BaseSelect.vue'
import InputText from 'primevue/inputtext'
import BaseButton from '@/components/common/ui/BaseButton.vue'

const props = defineProps<{
  dateRange: Date[] | null
  searchQuery: string
  filterMap: string | null
  filterProfession: string | null
  filterOptions: { maps: string[]; professions: string[] }
  loading: boolean
}>()

const emit = defineEmits<{
  'update:dateRange': [value: Date[] | null]
  'update:searchQuery': [value: string]
  'update:filterMap': [value: string | null]
  'update:filterProfession': [value: string | null]
  apply: []
  reset: []
}>()

const localDateRange = computed({ get: () => props.dateRange, set: v => emit('update:dateRange', v) })
const localSearch = computed({ get: () => props.searchQuery, set: v => emit('update:searchQuery', v) })
const localMap = computed({ get: () => props.filterMap, set: v => emit('update:filterMap', v) })
const localProfession = computed({ get: () => props.filterProfession, set: v => emit('update:filterProfession', v) })
</script>
