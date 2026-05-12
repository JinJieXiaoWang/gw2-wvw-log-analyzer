<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.5s"
  >
    <div class="flex flex-col lg:flex-row gap-4 items-end">
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">日期范围</label>
        <Calendar
          v-model="dateRange"
          selection-mode="range"
          date-format="yy-mm-dd"
          placeholder="选择日期范围"
          show-icon
          class="w-full"
        />
      </div>
      <div class="flex-1">
        <label class="block text-sm text-neutral-text-secondary mb-2">搜索账号或角色</label>
        <InputText
          v-model="searchQuery"
          placeholder="输入账号或角色名..."
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-40">
        <label class="block text-sm text-neutral-text-secondary mb-2">地图</label>
        <Dropdown
          v-model="filterMap"
          :options="maps"
          placeholder="全部地图"
          show-clear
          class="w-full"
        />
      </div>
      <div class="w-full lg:w-40">
        <label class="block text-sm text-neutral-text-secondary mb-2">职业</label>
        <Dropdown
          v-model="filterProfession"
          :options="professions"
          placeholder="全部职业"
          show-clear
          class="w-full"
        />
      </div>
      <BaseButton
        label="应用筛选"
        icon="pi pi-search"
        class="btn-game"
        :loading="loading"
        @click="handleApply"
      />
      <BaseButton
        label="重置"
        icon="pi pi-refresh"
        class="btn-ghost"
        :disabled="loading"
        @click="handleReset"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 考勤筛选器组件
 * 功能：提供日期范围、搜索、地图、职业筛选
 * 作者：Claude
 * 创建日期：2026-05-11
 */

import { ref, watch } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'

export interface FilterOptions {
  maps: string[]
  professions: string[]
}

const props = defineProps<{
  filterOptions: FilterOptions
  loading: boolean
}>()

const emit = defineEmits<{
  'apply': []
  'reset': []
}>()

const dateRange = defineModel<Date[] | null>('dateRange', { default: null })
const searchQuery = defineModel<string>('searchQuery', { default: '' })
const filterMap = defineModel<string | null>('filterMap', { default: null })
const filterProfession = defineModel<string | null>('filterProfession', { default: null })

const maps = props.filterOptions.maps
const professions = props.filterOptions.professions

const handleApply = () => emit('apply')
const handleReset = () => emit('reset')
</script>
