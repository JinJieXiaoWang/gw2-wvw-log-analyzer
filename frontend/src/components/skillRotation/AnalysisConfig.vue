<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.1s"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
        <i class="pi pi-cog text-primary" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-neutral-text">
          分析配置
        </h3>
        <p class="text-xs text-neutral-text-secondary">
          选择日志和玩家进行对比
        </p>
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">选择日志</label>
        <Dropdown
          v-model="selectedLog"
          :options="logOptions"
          option-label="label"
          option-value="value"
          placeholder="选择日志"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">选择玩家</label>
        <Dropdown
          v-model="selectedPlayer"
          :options="playerOptions"
          option-label="label"
          option-value="value"
          placeholder="选择玩家"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">对比模式</label>
        <Dropdown
          v-model="compareMode"
          :options="compareModeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">时间范围</label>
        <Dropdown
          v-model="timeRange"
          :options="timeRangeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 技能循环分析配置组件
 * 功能：提供分析配置选项
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'
import Dropdown from 'primevue/dropdown'

// Props
const props = defineProps<{
  logOptions: any[]
  playerOptions: any[]
}>()

// 确保props被使用
console.log(props.logOptions, props.playerOptions)

// Emits
const emit = defineEmits([
  'update:selected-log',
  'update:selected-player',
  'update:compare-mode',
  'update:time-range'
])

// 状态
const selectedLog = ref<string | null>(null)
const selectedPlayer = ref<string | null>(null)
const compareMode = ref('time')
const timeRange = ref('full')

// 选项数据
const compareModeOptions = [
  { label: '时间对比', value: 'time' },
  { label: '伤害对比', value: 'damage' },
  { label: '效率对比', value: 'efficiency' }
]

const timeRangeOptions = [
  { label: '完整战斗', value: 'full' },
  { label: '前5分钟', value: 'first5' },
  { label: '后5分钟', value: 'last5' }
]

// 监听状态变化
import { watch } from 'vue'

watch(selectedLog, (newValue) => {
  emit('update:selected-log', newValue)
})

watch(selectedPlayer, (newValue) => {
  emit('update:selected-player', newValue)
})

watch(compareMode, (newValue) => {
  emit('update:compare-mode', newValue)
})

watch(timeRange, (newValue) => {
  emit('update:time-range', newValue)
})
</script>