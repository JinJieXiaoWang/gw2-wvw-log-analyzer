<template>
  <Dialog
    :visible="visible"
    header="上传战斗日志"
    :modal="true"
    :style="{ width: '640px' }"
    :closable="!isUploading"
    class="custom-dialog"
    @update:visible="onVisibleChange"
  >
    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".zevtc"
      multiple
      class="hidden"
      @change="onFileSelect"
    >

    <div class="py-4">
      <!-- 拖拽上传区 -->
      <div
        v-if="selectedFiles.length === 0"
        class="border-2 border-dashed border-neutral-border rounded-2xl p-8 text-center transition-all cursor-pointer"
        :class="{ 'border-primary bg-primary/5 scale-[1.02]': isDragging }"
        @dragover.prevent="onDragOver"
        @dragleave="onDragLeave"
        @drop.prevent="onDrop"
        @click="triggerFileInput"
      >
        <div class="w-20 h-20 mx-auto bg-gradient-to-br from-primary/20 to-secondary/20 rounded-2xl flex items-center justify-center mb-4">
          <i class="pi pi-cloud-upload text-4xl text-primary" />
        </div>
        <p class="text-neutral-text text-lg font-medium mb-2">
          拖拽文件到此处或点击选择
        </p>
        <p class="text-xs text-neutral-text-secondary mb-4">
          支持 .zevtc 格式文件，最多可选择 100 个文件
        </p>
        <Button
          label="选择文件"
          icon="pi pi-folder-open"
          class="btn-game"
          @click.stop="triggerFileInput"
        />
      </div>

      <!-- 已选文件列表 -->
      <div
        v-if="selectedFiles.length > 0"
        class="mt-0 p-4 bg-neutral-bg rounded-xl border border-neutral-border"
      >
        <div class="flex items-center justify-between mb-3 pb-2 border-b border-neutral-border">
          <span class="text-sm text-neutral-text font-medium">
            已选择 {{ selectedFiles.length }} 个文件
            <span
              v-if="selectedFiles.length > 50"
              class="text-status-warning text-xs ml-1"
            >
              (批量上传建议不超过50个)
            </span>
          </span>
          <div class="flex items-center gap-2">
            <Button
              v-if="!isUploading"
              label="继续添加"
              icon="pi pi-plus"
              size="small"
              text
              @click="triggerFileInput"
            />
            <Button
              label="清空"
              size="small"
              text
              class="text-status-error"
              :disabled="isUploading"
              @click="clearFiles"
            />
          </div>
        </div>

        <!-- 文件列表（带进度） -->
        <div class="max-h-64 overflow-y-auto space-y-2">
          <div
            v-for="(file, index) in selectedFiles"
            :key="file.name + index"
            class="flex items-center gap-3 p-2 rounded-lg transition-colors"
            :class="{
              'bg-primary/5': uploadItems[index]?.phase === 'uploading',
              'bg-status-success/5': uploadItems[index]?.phase === 'success',
              'bg-status-error/5': uploadItems[index]?.phase === 'error',
            }"
          >
            <!-- 状态图标 -->
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="{
                'bg-primary/10': !uploadItems[index]?.phase || uploadItems[index]?.phase === 'pending',
                'bg-primary/20': uploadItems[index]?.phase === 'uploading',
                'bg-status-success/20': uploadItems[index]?.phase === 'success',
                'bg-status-error/20': uploadItems[index]?.phase === 'error' || uploadItems[index]?.phase === 'cancelled',
              }"
            >
              <i
                class="text-sm"
                :class="{
                  'pi pi-file text-primary': !uploadItems[index]?.phase || uploadItems[index]?.phase === 'pending',
                  'pi pi-spin pi-spinner text-primary': uploadItems[index]?.phase === 'uploading',
                  'pi pi-spin pi-spinner text-status-warning': uploadItems[index]?.phase === 'processing',
                  'pi pi-check text-status-success': uploadItems[index]?.phase === 'success',
                  'pi pi-times text-status-error': uploadItems[index]?.phase === 'error' || uploadItems[index]?.phase === 'cancelled',
                }"
              />
            </div>

            <!-- 文件名和大小 -->
            <div class="flex-1 min-w-0">
              <p class="text-sm text-neutral-text font-medium truncate">
                {{ file.name }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ formatFileSize(file.size) }}
                <span
                  v-if="uploadItems[index]?.phase === 'uploading' && uploadItems[index]?.transportPercent !== undefined"
                  class="text-primary ml-1"
                >
                  传输 {{ uploadItems[index].transportPercent }}%
                </span>
                <span
                  v-else-if="uploadItems[index]?.phase === 'processing'"
                  class="text-status-warning ml-1"
                >
                  服务器处理中...
                </span>
                <span
                  v-else-if="uploadItems[index]?.phase === 'success'"
                  class="text-status-success ml-1"
                >
                  完成
                </span>
                <span
                  v-else-if="uploadItems[index]?.phase === 'error'"
                  class="text-status-error ml-1"
                >
                  {{ uploadItems[index].errorMsg || '失败' }}
                </span>
              </p>
            </div>

            <!-- 单个文件进度条（仅当前上传文件显示） -->
            <div
              v-if="uploadItems[index]?.phase === 'uploading'"
              class="w-24 flex-shrink-0"
            >
              <div class="h-1.5 bg-neutral-border rounded-full overflow-hidden">
                <div
                  class="h-full bg-primary rounded-full transition-all duration-300"
                  :style="{ width: (uploadItems[index].transportPercent || 0) + '%' }"
                />
              </div>
            </div>

            <!-- 删除按钮 -->
            <Button
              v-if="!isUploading"
              icon="pi pi-times"
              size="small"
              text
              class="hover:bg-status-error/10 flex-shrink-0"
              @click="removeFile(index)"
            />
          </div>
        </div>
      </div>

      <!-- 总体上传进度 -->
      <div
        v-if="isUploading || uploadComplete"
        class="mt-4"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-neutral-text-secondary">
            <span v-if="uploadPhase === 'uploading'">
              正在上传 {{ currentUploadIndex + 1 }}/{{ selectedFiles.length }}
            </span>
            <span v-else-if="uploadPhase === 'processing'">
              服务器处理中 {{ currentUploadIndex + 1 }}/{{ selectedFiles.length }}
            </span>
            <span v-else-if="uploadPhase === 'completed'">
              上传完成
            </span>
          </span>
          <span class="text-sm text-neutral-text font-medium">{{ Math.round(overallProgress) }}%</span>
        </div>
        <div class="h-2 bg-neutral-border rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500 ease-out"
            :class="{
              'bg-primary': uploadPhase === 'uploading',
              'bg-status-warning': uploadPhase === 'processing' || (uploadPhase === 'completed' && failedCount > 0 && successCount > 0),
              'bg-status-success': uploadPhase === 'completed' && failedCount === 0,
              'bg-status-error': uploadPhase === 'completed' && failedCount > 0 && successCount === 0,
            }"
            :style="{ width: overallProgress + '%' }"
          />
        </div>
        <p
          v-if="uploadPhase === 'processing'"
          class="text-xs text-status-warning mt-2 flex items-center gap-1"
        >
          <i class="pi pi-spin pi-spinner" />
          文件已上传至服务器，正在解析和处理中，请稍候...
        </p>
        <p
          v-if="currentError"
          class="text-xs text-status-error mt-2"
        >
          {{ currentError }}
        </p>
      </div>

      <!-- 上传结果摘要 -->
      <div
        v-if="uploadComplete && selectedFiles.length > 0"
        class="mt-4 p-4 rounded-xl border"
        :class="{
          'bg-status-success/5 border-status-success/20': failedCount === 0,
          'bg-status-error/5 border-status-error/20': successCount === 0,
          'bg-status-warning/5 border-status-warning/20': successCount > 0 && failedCount > 0,
        }"
      >
        <div class="flex items-center gap-2 mb-2">
          <i
            class="text-lg"
            :class="{
              'pi pi-check-circle text-status-success': failedCount === 0,
              'pi pi-times-circle text-status-error': successCount === 0,
              'pi pi-exclamation-circle text-status-warning': successCount > 0 && failedCount > 0,
            }"
          />
          <span class="font-semibold text-neutral-text">
            {{ failedCount === 0 ? '全部上传成功' : successCount === 0 ? '全部上传失败' : '部分上传成功' }}
          </span>
        </div>
        <div class="text-sm text-neutral-text-secondary space-y-1">
          <p>成功: <span class="text-status-success font-medium">{{ successCount }}</span> 个</p>
          <p v-if="failedCount > 0">
            失败: <span class="text-status-error font-medium">{{ failedCount }}</span> 个
          </p>
          <div
            v-if="failedItems.length > 0"
            class="mt-2"
          >
            <p class="text-xs text-status-error">
              失败文件:
            </p>
            <ul class="text-xs text-status-error mt-1 space-y-0.5 max-h-24 overflow-y-auto">
              <li
                v-for="item in failedItems"
                :key="item.name"
              >
                {{ item.name }}: {{ item.error }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        label="取消"
        class="btn-ghost"
        :disabled="isUploading && uploadPhase !== 'completed'"
        @click="closeDialog"
      />
      <Button
        v-if="!uploadComplete"
        label="开始上传"
        icon="pi pi-upload"
        class="btn-game"
        :disabled="selectedFiles.length === 0 || isUploading"
        :loading="isUploading"
        @click="uploadFiles"
      />
      <Button
        v-else
        label="完成"
        icon="pi pi-check"
        class="btn-game"
        severity="success"
        @click="closeDialog"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 日志上传弹窗组件 v2.0
 * 功能：处理日志文件上传，支持批量上传，进度条同步优化
 * 更新：2026-05-06
 *   - 进度条分阶段显示（传输0-70% + 处理70-100%）
   - 每个文件独立状态跟踪
   - 优化多文件上传体验
 */

import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { logsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { formatBytes } from '@/utils/core/helpers'

type UploadPhase = 'idle' | 'uploading' | 'processing' | 'completed'

type FileUploadPhase = 'pending' | 'uploading' | 'processing' | 'success' | 'error' | 'cancelled'

interface UploadItem {
  phase: FileUploadPhase
  transportPercent: number
  overallPercent: number
  errorMsg?: string
}

defineProps<{
  visible: boolean
}>()

const toast = useToast()

const emit = defineEmits([
  'update:visible',
  'upload-success'
])

// ============================================
// 状态
// ============================================
const isDragging = ref(false)
const selectedFiles = ref<File[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

const uploadPhase = ref<UploadPhase>('idle')
const currentUploadIndex = ref(0)
const uploadItems = ref<UploadItem[]>([])
const currentError = ref('')
const uploadComplete = ref(false)

// ============================================
// 计算属性
// ============================================
const isUploading = computed(() => uploadPhase.value === 'uploading' || uploadPhase.value === 'processing')

const overallProgress = computed(() => {
  if (selectedFiles.value.length === 0) return 0
  const total = uploadItems.value.reduce((sum, item) => sum + (item?.overallPercent || 0), 0)
  return total / selectedFiles.value.length
})

const successCount = computed(() => uploadItems.value.filter(i => i?.phase === 'success').length)
const failedCount = computed(() => uploadItems.value.filter(i => i?.phase === 'error').length)
const failedItems = computed(() => {
  return uploadItems.value
    .map((item, idx) => ({ name: selectedFiles.value[idx]?.name, error: item?.errorMsg, phase: item?.phase }))
    .filter(i => i.phase === 'error')
})

// ============================================
// 文件选择
// ============================================
const formatFileSize = formatBytes

const triggerFileInput = () => {
  fileInput.value?.click()
}

const onFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    addFiles(Array.from(target.files))
    target.value = ''
  }
}

const addFiles = (files: File[]) => {
  const zevtcFiles = files.filter(f => f.name.endsWith('.zevtc'))
  const remainingSlots = 100 - selectedFiles.value.length
  const filesToAdd = zevtcFiles.slice(0, remainingSlots)

  if (zevtcFiles.length > remainingSlots) {
    toast.add({
      severity: 'warn',
      summary: '提示',
      detail: `最多支持100个文件，已自动截取前 ${remainingSlots} 个`,
      life: 4000
    })
  }

  filesToAdd.forEach(file => {
    if (!selectedFiles.value.some(f => f.name === file.name)) {
      selectedFiles.value.push(file)
    }
  })

  // 重置上传状态
  uploadComplete.value = false
  uploadPhase.value = 'idle'
  uploadItems.value = []
  currentError.value = ''
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
  uploadItems.value.splice(index, 1)
}

const clearFiles = () => {
  selectedFiles.value = []
  uploadItems.value = []
  uploadComplete.value = false
  uploadPhase.value = 'idle'
  currentError.value = ''
}

const onDragOver = () => { isDragging.value = true }
const onDragLeave = () => { isDragging.value = false }
const onDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

// ============================================
// 上传逻辑
// ============================================
const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return

  const totalFiles = selectedFiles.value.length
  uploadPhase.value = 'uploading'
  uploadComplete.value = false
  currentError.value = ''
  currentUploadIndex.value = 0

  // 初始化上传项状态
  uploadItems.value = selectedFiles.value.map(() => ({
    phase: 'pending' as FileUploadPhase,
    transportPercent: 0,
    overallPercent: 0,
  }))

  for (let i = 0; i < totalFiles; i++) {
    currentUploadIndex.value = i
    uploadItems.value[i].phase = 'uploading'

    // 阶段1：HTTP传输（0-70%）
    const onFileProgress = (singlePercent: number) => {
      uploadItems.value[i].transportPercent = singlePercent
      // 单个文件的传输占该文件总进度的 70%
      uploadItems.value[i].overallPercent = singlePercent * 0.7
      // 已完成的文件 + 当前文件进度 = 总体进度
    }

    const result = await uploadSingleFile(selectedFiles.value[i], onFileProgress)

    if (result.success) {
      uploadItems.value[i].phase = 'success'
      uploadItems.value[i].overallPercent = 100
    } else {
      uploadItems.value[i].phase = 'error'
      uploadItems.value[i].errorMsg = result.message
      uploadItems.value[i].overallPercent = 0
    }
  }

  uploadPhase.value = 'completed'
  uploadComplete.value = true

  if (successCount.value > 0) {
    emit('upload-success')
  }

  if (failedCount.value === 0) {
    toast.add({
      severity: 'success',
      summary: '上传成功',
      detail: `成功上传 ${successCount.value} 个文件`,
      life: 3000
    })
  } else if (successCount.value > 0) {
    toast.add({
      severity: 'warn',
      summary: '部分上传成功',
      detail: `成功 ${successCount.value} 个，失败 ${failedCount.value} 个`,
      life: 4000
    })
  } else {
    toast.add({
      severity: 'error',
      summary: '上传失败',
      detail: `${failedCount.value} 个文件上传失败`,
      life: 4000
    })
  }
}

const uploadSingleFile = async (
  file: File,
  onProgress?: (percent: number) => void
): Promise<{ success: boolean; message?: string }> => {
  try {
    const wrappedResult = await ApiResponseWrapper.wrap(
      logsService.uploadLog(file, { auto_parse: true }, onProgress),
      { showErrorMessage: false }
    )

    if (wrappedResult.success) {
      return { success: true }
    } else {
      return { success: false, message: wrappedResult.error?.message || '上传失败' }
    }
  } catch (error: any) {
    return { success: false, message: error.message || '上传失败' }
  }
}

// ============================================
// 弹窗控制
// ============================================
const onVisibleChange = (val: boolean) => {
  if (!val && isUploading.value) {
    // 上传中不允许关闭
    return
  }
  emit('update:visible', val)
}

const closeDialog = () => {
  if (isUploading.value && uploadPhase.value !== 'completed') {
    return
  }
  emit('update:visible', false)
  setTimeout(() => {
    // 关闭弹框时始终重置状态，避免下次打开还显示旧文件
    selectedFiles.value = []
    uploadItems.value = []
    uploadComplete.value = false
    uploadPhase.value = 'idle'
    currentError.value = ''
    currentUploadIndex.value = 0
  }, 300)
}
</script>
