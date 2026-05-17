<script setup lang="ts">
// 模块功能：技能循环分析配置组件
// 说明：从后端API获取真实日志列表和玩家列表

import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import { computed, onMounted, ref, watch } from 'vue'
import { logsService } from '@/services/combat/logsService'
import { apiFactory } from '@/services/core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'

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
  'update:compareMode': [value: string]
  'update:timeRange': [value: string]
  'analyze': []
}>()

const localLogId = ref(props.selectedLogId)
const localMemberId = ref(props.selectedMemberId)
const compareMode = ref('time')
const timeRange = ref('full')

// 日志列表
const logs = ref<any[]>([])
const logsLoading = ref(false)
// 玩家列表
const players = ref<any[]>([])
const playersLoading = ref(false)

const logOptions = computed(() => [
  { label: '选择一个日志', value: null },
  ...logs.value.map((log: any) => ({
    label: `${log.filename || log.fileName || '未命名日志'} (${log.id})`,
    value: String(log.id)
  }))
])

const playerOptions = computed(() => [
  { label: '选择一个玩家', value: null },
  ...players.value.map((p: any) => ({
    label: `${p.account} · ${p.profession}`,
    value: p.account
  }))
])

const compareModeOptions = [
  { label: '时间对比', value: 'time' },
  { label: '伤害对比', value: 'damage' },
  { label: '效率对比', value: 'efficiency' }
]

import { LOG_TIME_RANGE_OPTIONS } from '@/constants/options'
const timeRangeOptions = LOG_TIME_RANGE_OPTIONS

// 获取日志列表
async function fetchLogs() {
  logsLoading.value = true
  try {
    const response = await logsService.getLogs({ page: 1, page_size: 100 })
    if (response.success && response.data) {
      // 适配不同分页结构
      const items = response.data.items || response.data.list || response.data || []
      logs.value = Array.isArray(items) ? items : []
    }
  } catch (err) {
    console.error('获取日志列表失败:', err)
  } finally {
    logsLoading.value = false
  }
}

// 获取指定日志的玩家列表
async function fetchPlayers(logId: string | null) {
  if (!logId) {
    players.value = []
    return
  }
  playersLoading.value = true
  try {
    const response = await apiFactory.get<any>(`ei-analysis/${logId}`)
    if (response.success && response.data && response.data.players) {
      players.value = response.data.players
    } else {
      players.value = []
    }
  } catch (err) {
    console.error('获取玩家列表失败:', err)
    players.value = []
  } finally {
    playersLoading.value = false
  }
}

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
  // 日志改变时，重置玩家选择并获取新玩家列表
  localMemberId.value = null
  emit('update:selectedMemberId', null)
  fetchPlayers(newValue)
})

watch(localMemberId, (newValue) => {
  emit('update:selectedMemberId', newValue)
})

watch(compareMode, (newValue) => {
  emit('update:compareMode', newValue)
})

watch(timeRange, (newValue) => {
  emit('update:timeRange', newValue)
})

function handleAnalyze() {
  emit('analyze')
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="bg-neutral-bg-secondary rounded-xl p-4 border border-neutral-border/30">
    <div class="flex flex-wrap items-end gap-4">
      <!-- 日志选择 -->
      <div class="flex-1 min-w-[200px]">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">选择日志</label>
        <Dropdown
          v-model="localLogId"
          :options="logOptions"
          option-label="label"
          option-value="value"
          placeholder="选择一个日志"
          class="w-full"
          :loading="logsLoading"
          :disabled="disabled"
          scroll-height="250px"
        />
      </div>

      <!-- 玩家选择 -->
      <div class="flex-1 min-w-[200px]">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">选择玩家</label>
        <Dropdown
          v-model="localMemberId"
          :options="playerOptions"
          option-label="label"
          option-value="value"
          placeholder="选择一个玩家"
          class="w-full"
          :loading="playersLoading"
          :disabled="disabled || !localLogId"
          scroll-height="250px"
        />
      </div>

      <!-- 对比模式 -->
      <div class="w-[160px]">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">对比模式</label>
        <Dropdown
          v-model="compareMode"
          :options="compareModeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :disabled="disabled"
        />
      </div>

      <!-- 时间范围 -->
      <div class="w-[160px]">
        <label class="block text-sm text-neutral-text-secondary mb-1.5">时间范围</label>
        <Dropdown
          v-model="timeRange"
          :options="timeRangeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :disabled="disabled"
        />
      </div>

      <!-- 分析按钮 -->
      <Button
        label="执行分析"
        icon="pi pi-play"
        class="h-[42px] px-6"
        :loading="loading"
        :disabled="disabled || !localLogId || !localMemberId"
        @click="handleAnalyze"
      />
    </div>
  </div>
</template>
