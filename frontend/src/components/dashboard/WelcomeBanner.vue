<template>
  <div class="welcome-banner animate-slide-in-up">
    <div class="welcome-banner-content">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-secondary to-primary flex items-center justify-center shadow-lg float-element">
            <i class="pi pi-chart-bar text-3xl text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-neutral-text mb-1">
              指挥官战报
            </h1>
            <p class="text-neutral-text-secondary text-sm">
              WVW战场数据可视化分析
            </p>
          </div>
        </div>
        <div class="flex gap-3 items-center">
          <Dropdown
            v-model="localTimeRange"
            :options="timeRangeOptions"
            option-label="label"
            option-value="value"
            class="w-40"
            placeholder="选择时间"
            @change="changeTimeRange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 数据看板欢迎横幅组件
 * 功能：显示页面标题和操作按钮
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, watch } from 'vue'
import Dropdown from 'primevue/dropdown'

// Props
const props = defineProps<{
  timeRange: string
  timeRangeOptions: Array<{ label: string; value: string }>
}>()

// Emits
const emit = defineEmits<{
  'update:timeRange': [value: string]
}>()

// 本地状态
const localTimeRange = ref(props.timeRange)

// 监听props变化
watch(() => props.timeRange, (newValue) => {
  localTimeRange.value = newValue
})

// 事件处理
const changeTimeRange = () => {
  emit('update:timeRange', localTimeRange.value)
}
</script>