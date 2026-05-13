<template>
  <div
    v-if="files.length > 0"
    class="mt-0 p-4 bg-neutral-bg rounded-xl border border-neutral-border"
  >
    <div class="flex items-center justify-between mb-3 pb-2 border-b border-neutral-border">
      <span class="text-sm text-neutral-text font-medium">
        已上传 {{ files.length }} 个文件        <span
          v-if="files.length > 50"
          class="text-status-warning text-xs ml-1"
        >(批量上传建议不超50个)</span>
      </span>
      <div class="flex items-center gap-2">
        <BaseButton
          v-if="!isUploading"
          label="添加文件"
          icon="pi pi-plus"
          size="small"
          text
          @click="$emit('add')"
        />
        <BaseButton
          label="清空"
          size="small"
          text
          class="text-status-error"
          :disabled="isUploading"
          @click="$emit('clear')"
        />
      </div>
    </div>

    <div class="max-h-64 overflow-y-auto space-y-2">
      <div
        v-for="(file, index) in files"
        :key="file.name + index"
        class="flex items-center gap-3 p-2 rounded-lg transition-colors"
        :class="{
          'bg-primary/5': items[index]?.phase === 'uploading',
          'bg-status-success/5': items[index]?.phase === 'success',
          'bg-status-error/5': items[index]?.phase === 'error',
        }"
      >
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          :class="{
            'bg-primary/10': !items[index]?.phase || items[index]?.phase === 'pending',
            'bg-primary/20': items[index]?.phase === 'uploading',
            'bg-status-success/20': items[index]?.phase === 'success',
            'bg-status-error/20': items[index]?.phase === 'error' || items[index]?.phase === 'cancelled',
          }"
        >
          <i
            class="text-sm"
            :class="{
              'pi pi-file text-primary': !items[index]?.phase || items[index]?.phase === 'pending',
              'pi pi-spin pi-spinner text-primary': items[index]?.phase === 'uploading',
              'pi pi-spin pi-spinner text-status-warning': items[index]?.phase === 'processing',
              'pi pi-check text-status-success': items[index]?.phase === 'success',
              'pi pi-times text-status-error': items[index]?.phase === 'error' || items[index]?.phase === 'cancelled',
            }"
          />
        </div>

        <div class="flex-1 min-w-0">
          <p class="text-sm text-neutral-text font-medium truncate">
            {{ file.name }}
          </p>
          <p class="text-xs text-neutral-text-secondary">
            {{ formatSize(file.size) }}
            <span
              v-if="items[index]?.phase === 'uploading' && items[index]?.transportPercent !== undefined"
              class="text-primary ml-1"
            >传输 {{ items[index].transportPercent }}%</span>
            <span
              v-else-if="items[index]?.phase === 'processing'"
              class="text-status-warning ml-1"
            >服务器处理中...</span>
            <span
              v-else-if="items[index]?.phase === 'success'"
              class="text-status-success ml-1"
            >完成</span>
            <span
              v-else-if="items[index]?.phase === 'error'"
              class="text-status-error ml-1"
            >{{ items[index].errorMsg || 'ʧ败' }}</span>
          </p>
        </div>

        <div
          v-if="items[index]?.phase === 'uploading'"
          class="w-24 flex-shrink-0"
        >
          <div class="h-1.5 bg-neutral-border rounded-full overflow-hidden">
            <div
              class="h-full bg-primary rounded-full transition-all duration-300"
              :style="{ width: (items[index].transportPercent || 0) + '%' }"
            />
          </div>
        </div>

        <BaseButton
          v-if="!isUploading"
          icon="pi pi-times"
          size="small"
          text
          class="hover:bg-status-error/10 flex-shrink-0"
          @click="$emit('remove', index)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue';

interface UploadItem {
  phase?: string
  transportPercent?: number
  errorMsg?: string
}

defineProps<{
  files: File[]
  items: UploadItem[]
  isUploading: boolean
  formatSize: (size: number) => string
}>()

defineEmits<{
  (e: 'add'): void
  (e: 'clear'): void
  (e: 'remove', index: number): void
}>()
</script>
