<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-neutral-text">
        dps.report API 测试
      </h1>
      <p class="text-neutral-text-secondary text-sm mt-1">
        上传 zevtc 文件到 dps.report，测试 EI 解析响应速度和数据完整性
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
          点击或拖拽上传 zevtc 文件
        </p>
        <p class="text-neutral-text-secondary text-xs mt-1">
          支持 .zevtc / .evtc / .evtc.zip
        </p>
        <input
          ref="fileInput"
          type="file"
          accept=".zevtc,.evtc,.evtc.zip"
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
          label="开始测试"
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
        <i class="pi pi-clock text-primary" /> 耗时统计
      </h3>

      <div
        v-if="loading"
        class="flex items-center gap-3"
      >
        <ProgressSpinner style="width: 24px; height: 24px" />
        <span class="text-sm text-neutral-text-secondary">正在上传到 dps.report 并等待解析...</span>
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
            上传耗时
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.json_fetch_time_ms }}ms
          </p>
          <p class="text-xs text-neutral-text-secondary">
            JSON拉取
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.total_time_ms }}ms
          </p>
          <p class="text-xs text-neutral-text-secondary">
            总耗时
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.ei_version || '-' }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            EI 版本
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
        <i class="pi pi-chart-bar text-primary" /> 数据概览
      </h3>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.player_count }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            玩家数
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.target_count }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            目标数
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <p class="text-xl font-bold text-primary">
            {{ result.skill_map_count }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            技能映射
          </p>
        </div>
        <div class="text-center p-3 rounded bg-neutral-bg">
          <a
            :href="result.permalink"
            target="_blank"
            class="text-sm text-primary hover:underline"
          >
            查看报告 <i class="pi pi-external-link text-xs" />
          </a>
          <p class="text-xs text-neutral-text-secondary">
            dps.report
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
            技能循环 {{ result.has_rotation ? '✓' : '✗' }}
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
            武器配置 {{ result.has_weapons ? '✓' : '✗' }}
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
            死亡回放 {{ result.has_death_recap ? '✓' : '✗' }}
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
        <i class="pi pi-code text-primary" /> 数据预览
      </h3>

      <!-- 技能循环预览 -->
      <div v-if="result.has_rotation">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          技能循环 (前3条)
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_rotation_preview, null, 2) }}</pre>
        </div>
      </div>

      <!-- 武器配置预览 -->
      <div v-if="result.has_weapons">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          武器配置
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_weapons_preview, null, 2) }}</pre>
        </div>
      </div>

      <!-- 死亡回放预览 -->
      <div v-if="result.has_death_recap">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          死亡回放
        </h4>
        <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]">
          <pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_death_recap_preview, null, 2) }}</pre>
        </div>
      </div>

      <!-- SkillMap 预览 -->
      <div v-if="result.skill_map_count > 0">
        <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">
          SkillMap 前10个key
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

const toast = useToast()
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const loading = ref(false)
const result = ref<Record<string, any> | null>(null)

const fmtSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
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
      timeout: 300000, // 5分钟
    })

    if (res.success && res.data) {
      result.value = res.data as Record<string, any>
      toast.add({ severity: 'success', summary: '测试完成', detail: `总耗时 ${(res.data as Record<string, any>).total_time_ms}ms`, life: 3000 })
    } else {
      toast.add({ severity: 'error', summary: '测试失败', detail: res.message || '未知错误', life: 5000 })
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '请求失败', detail: e.message || '网络错误', life: 5000 })
  } finally {
    loading.value = false
  }
}
</script>
