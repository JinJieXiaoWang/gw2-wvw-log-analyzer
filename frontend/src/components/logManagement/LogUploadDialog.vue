<template>
  <Dialog
    :visible="visible"
    header="上传战斗日志"
    :modal="true"
    :style="{ width: '600px' }"
    :closable="true"
    class="custom-dialog"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="py-4">
      <div
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
          支持 .zevtc 格式文件，可批量选择多个文件
        </p>
        <input
          ref="fileInput"
          type="file"
          accept=".zevtc"
          multiple
          class="hidden"
          @change="onFileSelect"
        >
        <Button
          label="选择文件"
          icon="pi pi-folder-open"
          class="btn-game"
          @click.stop="triggerFileInput"
        />
      </div>

      <div
        v-if="selectedFiles.length > 0"
        class="mt-4 p-4 bg-neutral-bg rounded-xl border border-neutral-border max-h-60 overflow-y-auto"
      >
        <div class="flex items-center justify-between mb-3 pb-2 border-b border-neutral-border">
          <span class="text-sm text-neutral-text font-medium">
            已选择 {{ selectedFiles.length }} 个文件
          </span>
          <Button
            label="清空"
            size="small"
            text
            class="text-status-error"
            @click="clearFiles"
          />
        </div>
        <div
          v-for="(file, index) in selectedFiles"
          :key="index"
          class="flex items-center justify-between py-2 border-b border-neutral-border/50 last:border-0"
        >
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <i class="pi pi-file text-primary" />
            </div>
            <div>
              <p class="text-sm text-neutral-text font-medium truncate max-w-xs">
                {{ file.name }}
              </p>
              <p class="text-xs text-neutral-text-secondary">
                {{ formatFileSize(file.size) }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-if="uploadStatuses[index] === 'uploading'"
              class="text-xs text-primary"
            >
              <i class="pi pi-spin pi-spinner" />
            </span>
            <span
              v-else-if="uploadStatuses[index] === 'success'"
              class="text-xs text-status-success"
            >
              <i class="pi pi-check-circle" />
            </span>
            <span
              v-else-if="uploadStatuses[index] === 'error'"
              class="text-xs text-status-error"
            >
              <i class="pi pi-times-circle" />
            </span>
            <Button
              icon="pi pi-times"
              size="small"
              text
              class="hover:bg-status-error/10"
              @click="removeFile(index)"
            />
          </div>
        </div>
      </div>

      <div
        v-if="isUploading"
        class="mt-4"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-neutral-text-secondary">
            正在上传 {{ currentUploadIndex + 1 }}/{{ selectedFiles.length }}
          </span>
          <span class="text-sm text-neutral-text font-medium">{{ uploadProgress }}%</span>
        </div>
        <div class="game-progress">
          <div
            class="game-progress-primary"
            :style="{ width: uploadProgress + '%' }"
          />
        </div>
        <p
          v-if="uploadError"
          class="text-xs text-status-error mt-2"
        >
          {{ uploadError }}
        </p>
      </div>

      <div
        v-if="uploadResults.length > 0"
        class="mt-4 p-4 bg-neutral-bg rounded-xl border border-neutral-border"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-neutral-text font-medium">
            上传结果
          </span>
          <span class="text-xs text-neutral-text-secondary">
            成功 {{ successCount }} 个，失败 {{ failedCount }} 个
          </span>
        </div>
      </div>
    </div>
    <template #footer>
      <Button
        label="取消"
        class="btn-ghost"
        :disabled="isUploading"
        @click="closeDialog"
      />
      <Button
        label="开始上传"
        icon="pi pi-upload"
        class="btn-game"
        :disabled="selectedFiles.length === 0 || isUploading"
        :loading="isUploading"
        @click="uploadFiles"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 日志上传弹窗组件
 * 功能：处理日志文件上传，支持批量上传
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { logsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { formatBytes } from '@/utils/core/helpers'

defineProps<{
  visible: boolean
}>()

const toast = useToast()

const emit = defineEmits([
  'update:visible',
  'upload-success'
])

const isDragging = ref(false)
const selectedFiles = ref<File[]>([])
const uploadProgress = ref(0)
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const currentUploadIndex = ref(0)
const uploadError = ref('')
const uploadStatuses = ref<Record<number, 'pending' | 'uploading' | 'success' | 'error'>>({})
const uploadResults = ref<Array<{ name: string; success: boolean; message?: string }>>([])

const successCount = computed(() => uploadResults.value.filter(r => r.success).length)
const failedCount = computed(() => uploadResults.value.filter(r => !r.success).length)

const formatFileSize = formatBytes

const triggerFileInput = () => {
  fileInput.value?.click()
}

const onFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    addFiles(Array.from(target.files))
  }
}

const addFiles = (files: File[]) => {
  const zevtcFiles = files.filter(f => f.name.endsWith('.zevtc'))
  zevtcFiles.forEach(file => {
    if (!selectedFiles.value.some(f => f.name === file.name)) {
      selectedFiles.value.push(file)
      uploadStatuses.value[selectedFiles.value.length - 1] = 'pending'
    }
  })
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
  const newStatuses: Record<number, 'pending' | 'uploading' | 'success' | 'error'> = {}
  selectedFiles.value.forEach((_, i) => {
    newStatuses[i] = uploadStatuses.value[i] || 'pending'
  })
  uploadStatuses.value = newStatuses
}

const clearFiles = () => {
  selectedFiles.value = []
  uploadStatuses.value = {}
  uploadResults.value = []
}

const onDragOver = () => {
  isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return

  const totalFiles = selectedFiles.value.length
  isUploading.value = true
  uploadError.value = ''
  uploadResults.value = []
  currentUploadIndex.value = 0
  uploadProgress.value = 0

  for (let i = 0; i < totalFiles; i++) {
    currentUploadIndex.value = i
    uploadStatuses.value[i] = 'uploading'

    // 构建整体进度回调：将单个文件进度映射为总进度
    const onFileProgress = (singlePercent: number) => {
      const overallPercent = Math.round(((i + singlePercent / 100) / totalFiles) * 100)
      uploadProgress.value = overallPercent
    }

    const result = await uploadSingleFile(selectedFiles.value[i], onFileProgress)

    if (result.success) {
      uploadStatuses.value[i] = 'success'
      uploadResults.value.push({ name: selectedFiles.value[i].name, success: true })
    } else {
      uploadStatuses.value[i] = 'error'
      uploadResults.value.push({ name: selectedFiles.value[i].name, success: false, message: result.message })
    }
  }

  // 确保进度条到达100%
  uploadProgress.value = 100

  if (successCount.value > 0 && failedCount.value === 0) {
    // 全部成功
    emit('upload-success')
    if (totalFiles > 1) {
      // 多文件：短暂停留让用户看到100%完成状态，再关闭弹窗
      await new Promise(resolve => setTimeout(resolve, 600))
    }
    isUploading.value = false
    toast.add({
      severity: 'success',
      summary: '上传成功',
      detail: `成功上传 ${successCount.value} 个文件`,
      life: 3000
    })
    closeDialog()
  } else if (successCount.value > 0 && failedCount.value > 0) {
    // 部分成功
    emit('upload-success')
    if (totalFiles > 1) {
      await new Promise(resolve => setTimeout(resolve, 600))
    }
    isUploading.value = false
    toast.add({
      severity: 'warn',
      summary: '部分上传成功',
      detail: `成功 ${successCount.value} 个，失败 ${failedCount.value} 个`,
      life: 4000
    })
    closeDialog()
  } else {
    // 全部失败：保持弹窗打开以便用户查看错误
    isUploading.value = false
    toast.add({
      severity: 'error',
      summary: '上传失败',
      detail: `${failedCount.value} 个文件上传失败，请检查后重试`,
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
      logsService.uploadLog(file, {
        auto_parse: true
      }, onProgress),
      {
        showErrorMessage: false
      }
    )

    if (wrappedResult.success) {
      return { success: true }
    } else {
      const errorMsg = wrappedResult.error?.message || '上传失败'
      return { success: false, message: errorMsg }
    }
  } catch (error: any) {
    return { success: false, message: error.message || '上传失败' }
  }
}

const closeDialog = () => {
  emit('update:visible', false)
  setTimeout(() => {
    selectedFiles.value = []
    uploadStatuses.value = {}
    uploadResults.value = []
    uploadProgress.value = 0
    isUploading.value = false
    uploadError.value = ''
    currentUploadIndex.value = 0
  }, 300)
}
</script>