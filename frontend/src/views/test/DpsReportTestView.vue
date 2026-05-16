<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-neutral-text">
        {{ PAGE_TITLE }}
      </h1>
      <p class="text-neutral-text-secondary text-sm mt-1">
        {{ PAGE_SUBTITLE }}
      </p>
    </div>

    <!-- 上传区域 -->
    <div class="card p-6">
      <div
        class="border-2 border-dashed border-neutral-border rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-primary hover:bg-primary/5"
        :class="{ 'border-primary bg-primary/5': isDragging }"
        @dragenter.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @dragover.prevent
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <i class="pi pi-cloud-upload text-4xl text-primary mb-3 block" />
        <p class="text-neutral-text font-medium">
          {{ UPLOAD_PROMPT }}
        </p>
        <p class="text-neutral-text-secondary text-xs mt-1">
          {{ FILE_TYPE_HINT }}
        </p>
        <input
          ref="fileInput"
          type="file"
          :accept="UPLOAD_ACCEPT_TYPES"
          class="hidden"
          @change="onFileChange"
        >
      </div>

      <div
        v-if="selectedFile"
        class="mt-4 flex items-center gap-3 p-3 rounded bg-neutral-bg"
      >
        <i class="pi pi-file text-primary" />
        <div class="flex-1 min-w-0">
          <p class="text-sm text-neutral-text truncate">
            {{ selectedFile.name }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ fmtSize(selectedFile.size) }}
          </p>
        </div>
        <BaseButton
          :label="START_TEST_LABEL"
          icon="pi pi-play"
          :loading="loading"
          @click="startTest"
        />
      </div>
    </div>

    <!-- 进度/耗时 -->
    <div
      v-if="loading || result"
      class="card p-6"
    >
      <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
        <i class="pi pi-clock text-primary" /> {{ TIME_STATS_TITLE }}
      </h3>

      <div
        v-if="loading"
        class="flex items-center gap-3"
      >
        <ProgressSpinner class="w-6 h-6" />
        <span class="text-sm text-neutral-text-secondary">{{ UPLOADING_STATUS }}</span>
      </div>

      <div
        v-else-if="result"
        class="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.upload_time_ms }}ms
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ UPLOAD_TIME_LABEL }}
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.json_fetch_time_ms }}ms
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ JSON_FETCH_LABEL }}
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.total_time_ms }}ms
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ TOTAL_TIME_LABEL }}
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.ei_version || '-' }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ EI_VERSION_LABEL }}
          </p>
        </div>
      </div>
    </div>

    <!-- 数据概览 -->
    <div
      v-if="result"
      class="card p-6"
    >
      <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
        <i class="pi pi-chart-bar text-primary" /> {{ DATA_OVERVIEW_TITLE }}
      </h3>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.player_count }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ PLAYER_COUNT_LABEL }}
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.target_count }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ TARGET_COUNT_LABEL }}
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.skill_map_count }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ SKILL_MAP_LABEL }}
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <a
            :href="result.permalink"
            target="_blank"
            class="text-sm text-primary hover:underline"
          >
            {{ VIEW_REPORT_LABEL }} <i class="pi pi-external-link text-xs" />
          </a>
          <p class="text-xs text-neutral-text-secondary">
            {{ DPS_REPORT_SOURCE }}
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          class="flex items-center gap-2 p-3 rounded"
          :class="result.has_rotation ? 'bg-status-success/10' : 'bg-status-error/10'"
        >
          <i
            class="pi"
            :class="result.has_rotation ? 'pi-check-circle text-status-success' : 'pi-times-circle text-status-error'"
          />
          <span
            class="text-sm"
            :class="result.has_rotation ? 'text-status-success' : 'text-status-error'"
          >
            {{ SKILL_ROTATION_LABEL }} {{ result.has_rotation ? CHECK_MARK : CROSS_MARK }}
          </span>
        </div>
        <div
          class="flex items-center gap-2 p-3 rounded"
          :class="result.has_weapons ? 'bg-status-success/10' : 'bg-status-error/10'"
        >
          <i
            class="pi"
            :class="result.has_weapons ? 'pi-check-circle text-status-success' : 'pi-times-circle text-status-error'"
          />
          <span
            class="text-sm"
            :class="result.has_weapons ? 'text-status-success' : 'text-status-error'"
          >
            {{ WEAPON_CONFIG_LABEL }} {{ result.has_weapons ? CHECK_MARK : CROSS_MARK }}
          </span>
        </div>
        <div
          class="flex items-center gap-2 p-3 rounded"
          :class="result.has_death_recap ? 'bg-status-success/10' : 'bg-status-error/10'"
        >
          <i
            class="pi"
            :class="result.has_death_recap ? 'pi-check-circle text-status-success' : 'pi-times-circle text-status-error'"
          />
          <span
            class="text-sm"
            :class="result.has_death_recap ? 'text-status-success' : 'text-status-error'"
          >
            {{ DEATH_RECAP_LABEL }} {{ result.has_death_recap ? CHECK_MARK : CROSS_MARK }}
          </span>
        </div>
      </div>
    </div>

    <!-- 数据预览 -->
    <div
      v-if="result?.raw_json"
      class="card p-6 space-y-4"
    >
      <h3 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2">
        <i class="pi pi-code text-primary" /> {{ PREVIEW_TITLE }}
      </h3>

      <!-- 技能循环预览 -->
      <div v-if="result.has_rotation">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          {{ ROTATION_PREVIEW_TITLE }}
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_rotation_preview, null, 2) }}</pre>
        </div>
      </div>

      <!-- 武器配置预览 -->
      <div v-if="result.has_weapons">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          {{ WEAPONS_PREVIEW_TITLE }}
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_weapons_preview, null, 2) }}</pre>
        </div>
      </div>

      <!-- 死亡回放预览 -->
      <div v-if="result.has_death_recap">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          {{ DEATH_RECAP_PREVIEW_TITLE }}
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_death_recap_preview, null, 2) }}</pre>
        </div>
      </div>

      <!-- SkillMap 预览 -->
      <div v-if="result.skill_map_count > 0">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          {{ SKILL_MAP_PREVIEW_TITLE }}
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.skill_map_keys, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import ProgressSpinner from 'primevue/progressspinner'
import { apiFactory } from '@/services/core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import { useToast } from 'primevue/usetoast'

// ========== 常量定义 ==========

// 页面文案
const PAGE_TITLE = 'dps.report API 测试'
const PAGE_SUBTITLE = '上传 zevtc 文件到 dps.report，测试 EI 解析响应速度和数据完整性'

// 上传区域文案
const UPLOAD_PROMPT = '点击或拖拽上传 zevtc 文件'
const UPLOAD_ACCEPT_TYPES = '.zevtc,.evtc,.evtc.zip'
const FILE_TYPE_HINT = '支持 .zevtc / .evtc / .evtc.zip'
const START_TEST_LABEL = '开始测试'

// 耗时统计文案
const TIME_STATS_TITLE = '耗时统计'
const UPLOADING_STATUS = '正在上传到 dps.report 并等待解析...'
const UPLOAD_TIME_LABEL = '上传耗时'
const JSON_FETCH_LABEL = 'JSON拉取'
const TOTAL_TIME_LABEL = '总耗时'
const EI_VERSION_LABEL = 'EI 版本'

// 数据概览文案
const DATA_OVERVIEW_TITLE = '数据概览'
const PLAYER_COUNT_LABEL = '玩家数'
const TARGET_COUNT_LABEL = '目标数'
const SKILL_MAP_LABEL = '技能映射'
const VIEW_REPORT_LABEL = '查看报告'
const DPS_REPORT_SOURCE = 'dps.report'
const SKILL_ROTATION_LABEL = '技能循环'
const WEAPON_CONFIG_LABEL = '武器配置'
const DEATH_RECAP_LABEL = '死亡回放'
const CHECK_MARK = '✓'
const CROSS_MARK = '✗'

// 数据预览文案
const PREVIEW_TITLE = '数据预览'
const ROTATION_PREVIEW_TITLE = '技能循环 (前3条)'
const WEAPONS_PREVIEW_TITLE = '武器配置'
const DEATH_RECAP_PREVIEW_TITLE = '死亡回放'
const SKILL_MAP_PREVIEW_TITLE = 'SkillMap 前10个key'

// 阈值
const REQUEST_TIMEOUT_MS = 300000 // 5分钟
const BYTES_PER_KB = 1024
const BYTES_PER_MB = 1024 * 1024

// Toast 配置
const TOAST_LIFE_SHORT = 3000
const TOAST_LIFE_LONG = 5000

// Toast 消息
const TEST_SUCCESS_SUMMARY = '测试完成'
const TEST_FAILED_SUMMARY = '测试失败'
const REQUEST_FAILED_SUMMARY = '请求失败'
const UNKNOWN_ERROR_DETAIL = '未知错误'
const NETWORK_ERROR_DETAIL = '网络错误'

// ========== 逻辑 ==========

const toast = useToast()
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const loading = ref(false)
const result = ref<Record<string, any> | null>(null)

const fmtSize = (bytes: number) => {
  if (bytes < BYTES_PER_KB) return bytes + ' B'
  if (bytes < BYTES_PER_MB) return (bytes / BYTES_PER_KB).toFixed(1) + ' KB'
  return (bytes / BYTES_PER_MB).toFixed(2) + ' MB'
}

const onDrop = (e: DragEvent) => {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    result.value = null
  }
}

const onFileChange = (e: Event) => {
  const files = (e.target as HTMLInputElement).files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    result.value = null
  }
}

const startTest = async () => {
  if (!selectedFile.value) return
  loading.value = true
  result.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const res = await apiFactory.post(API_ENDPOINTS.TEST.DPS_REPORT, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: REQUEST_TIMEOUT_MS,
    })

    if (res.success && res.data) {
      result.value = res.data as Record<string, any>
      toast.add({ severity: 'success', summary: TEST_SUCCESS_SUMMARY, detail: `总耗时 ${(res.data as Record<string, any>).total_time_ms}ms`, life: TOAST_LIFE_SHORT })
    } else {
      toast.add({ severity: 'error', summary: TEST_FAILED_SUMMARY, detail: res.message || UNKNOWN_ERROR_DETAIL, life: TOAST_LIFE_LONG })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: REQUEST_FAILED_SUMMARY, detail: e.message || NETWORK_ERROR_DETAIL, life: TOAST_LIFE_LONG })
  } finally {
    loading.value = false
  }
}
</script>
