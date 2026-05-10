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
    <input ref="fileInput" type="file" accept=".zevtc" multiple class="hidden" @change="onFileSelect">

    <div class="py-4">
      <UploadDropZone
        :files="selectedFiles"
        :is-dragging="isDragging"
        @trigger="triggerFileInput"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      />

      <UploadFileList
        :files="selectedFiles"
        :items="uploadItems"
        :is-uploading="isUploading"
        :format-size="formatFileSize"
        @add="triggerFileInput"
        @clear="clearFiles"
        @remove="removeFile"
      />

      <!-- 总体进度 -->
      <div v-if="isUploading || uploadComplete" class="mt-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-neutral-text-secondary">
            <span v-if="uploadPhase === 'uploading'">正在上传 {{ currentUploadIndex + 1 }}/{{ selectedFiles.length }}</span>
            <span v-else-if="uploadPhase === 'processing'">服务器处理中 {{ currentUploadIndex + 1 }}/{{ selectedFiles.length }}</span>
            <span v-else-if="uploadPhase === 'completed'">上传完成</span>
          </span>
          <span class="text-sm text-neutral-text font-medium">{{ Math.round(overallProgress) }}%</span>
        </div>
        <div class="h-2 bg-neutral-border rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-500 ease-out" :class="progressBarClass" :style="{ width: overallProgress + '%' }" />
        </div>
        <p v-if="uploadPhase === 'processing'" class="text-xs text-status-warning mt-2 flex items-center gap-1">
          <i class="pi pi-spin pi-spinner" />
          文件已上传至服务器，正在解析和处理中，请稍候.....
        </p>
        <p v-if="currentError" class="text-xs text-status-error mt-2">{{ currentError }}</p>
      </div>

      <UploadResultSummary
        :complete="uploadComplete"
        :files="selectedFiles"
        :success-count="successCount"
        :failed-count="failedCount"
        :failed-items="failedItems"
      />
    </div>

    <template #footer>
      <BaseButton label="取消" class="btn-ghost" :disabled="isUploading && uploadPhase !== 'completed'" @click="closeDialog" />
      <BaseButton
        v-if="!uploadComplete"
        label="开始上传"
        icon="pi pi-upload"
        class="btn-game"
        :disabled="selectedFiles.length === 0 || isUploading"
        :loading="isUploading"
        @click="uploadFiles"
      />
      <BaseButton v-else label="完成" icon="pi pi-check" class="btn-game" severity="success" @click="closeDialog" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import BaseButton from '@/components/common/ui/BaseButton.vue'
import { useLogUpload } from '@/composables/log/useLogUpload'
import UploadDropZone from './upload/UploadDropZone.vue'
import UploadFileList from './upload/UploadFileList.vue'
import UploadResultSummary from './upload/UploadResultSummary.vue'

defineProps<{ visible: boolean }>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'upload-success'): void
}>()

const {
  isDragging, selectedFiles, fileInput, uploadPhase, currentUploadIndex,
  uploadItems, currentError, uploadComplete, isUploading, overallProgress,
  successCount, failedCount, failedItems, formatFileSize, triggerFileInput,
  onFileSelect, removeFile, clearFiles, onDragOver, onDragLeave, onDrop,
  uploadFiles, reset,
} = useLogUpload({ onUploadSuccess: () => emit('upload-success') })

const progressBarClass = computed(() => {
  if (uploadPhase.value === 'uploading') return 'bg-primary'
  if (uploadPhase.value === 'processing' || (uploadPhase.value === 'completed' && failedCount.value > 0 && successCount.value > 0)) return 'bg-status-warning'
  if (uploadPhase.value === 'completed' && failedCount.value === 0) return 'bg-status-success'
  if (uploadPhase.value === 'completed' && failedCount.value > 0 && successCount.value === 0) return 'bg-status-error'
  return 'bg-primary'
})

const onVisibleChange = (val: boolean) => {
  if (!val && isUploading.value) return
  emit('update:visible', val)
}

const closeDialog = () => {
  if (isUploading.value && uploadPhase.value !== 'completed') return
  emit('update:visible', false)
  setTimeout(() => reset(), 300)
}
</script>
