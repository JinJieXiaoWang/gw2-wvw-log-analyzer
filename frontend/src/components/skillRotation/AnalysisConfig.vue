<script setup lang="ts">
// 模块功能：技能循环分析配置组件
// 作者：帅姐姐
// 创建日期：2026-04-27
// 更新日期：2026-05-14

import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import { computed, ref, watch } from 'vue'

interface Props {
  modelValue?: any
  selectedLogId?: string | null
  selectedMemberId?: string | null
  loading?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selectedLogId: null,
  selectedMemberId: null,
  loading: false,
  disabled: false
})

const emit = defineEmits<{
  'update:selectedLogId': [value: string | null]
  'update:selectedMemberId': [value: string | null]
  'analyze': []
}>()

const localLogId = ref(props.selectedLogId)
const localMemberId = ref(props.selectedMemberId)
const compareMode = ref('time')
const timeRange = ref('full')

const logOptions = computed(() => [
  { label: '选择一个日志', value: null },
  { label: '示例日志 1', value: '1' },
  { label: '示例日志 2', value: '2' }
])

const playerOptions = computed(() => [
  { label: '选择一个玩家', value: null },
  { label: '玩家 A', value: '1' },
  { label: '玩家 B', value: '2' }
])

const compareModeOptions = [
  { label: '时间对比', value: 'time' },
  { label: '伤害对比', value: 'damage' },
  { label: '效率对比', value: 'efficiency' }
]

import { LOG_TIME_RANGE_OPTIONS } from '@/constants/options'
const timeRangeOptions = LOG_TIME_RANGE_OPTIONS

watch(
  () => props.selectedLogId,
  (newValue) => {
    localLogId.value = newValue
  }
)

watch(
  () => props.selectedMemberId,
  (newValue) => {
    localMemberId.value = newValue
  }
)

watch(localLogId, (newValue) => {
  emit('update:selectedLogId', newValue)
})

watch(localMemberId, (newValue) => {
  emit('update:selectedMemberId', newValue)
})

function handleAnalyze() {
  emit('analyze')
}
</script>

<template>
  <div class="analysis-config bg-[#1a1a1e] border border-[#2a2a2e] rounded-lg p-4">
    <div class="flex items-center gap-3 mb-4">
      <div
        class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#165DFF]/30 to-[#FF7D00]/30 flex items-center justify-center"
      >
        <i class="pi pi-cog text-[#165DFF]" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-white">
          分析配置
        </h3>
        <p class="text-xs text-[#909399]">
          选择日志和玩家进行技能循环分析
        </p>
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div>
        <label class="block text-sm text-[#909399] mb-2">选择日志</label>
        <Dropdown
          v-model="localLogId"
          :options="logOptions"
          option-label="label"
          option-value="value"
          placeholder="选择日志"
          class="w-full"
          :disabled="loading"
        />
      </div>
      <div>
        <label class="block text-sm text-[#909399] mb-2">选择玩家</label>
        <Dropdown
          v-model="localMemberId"
          :options="playerOptions"
          option-label="label"
          option-value="value"
          placeholder="选择玩家"
          class="w-full"
          :disabled="loading"
        />
      </div>
      <div>
        <label class="block text-sm text-[#909399] mb-2">对比模式</label>
        <Dropdown
          v-model="compareMode"
          :options="compareModeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :disabled="loading"
        />
      </div>
      <div>
        <label class="block text-sm text-[#909399] mb-2">时间范围</label>
        <Dropdown
          v-model="timeRange"
          :options="timeRangeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :disabled="loading"
        />
      </div>
      <div class="flex items-end">
        <Button
          label="分析"
          icon="pi pi-refresh"
          :loading="loading"
          :disabled="disabled || loading"
          class="w-full"
          :pt="{
            root: { class: 'bg-[#165DFF] hover:bg-[#0f4cd9] text-white' }
          }"
          @click="handleAnalyze"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="postcss"></style>
