<template>
  <div v-if="complete && files.length > 0" class="mt-4 p-4 rounded-xl border" :class="resultClass">
    <div class="flex items-center gap-2 mb-2">
      <i class="text-lg" :class="iconClass" />
      <span class="font-semibold text-neutral-text">{{ resultTitle }}</span>
    </div>
    <div class="text-sm text-neutral-text-secondary space-y-1">
      <p>成功: <span class="text-status-success font-medium">{{ successCount }}</span> 个</p>
      <p v-if="failedCount > 0">ʧ败: <span class="text-status-error font-medium">{{ failedCount }}</span> 个</p>
      <div v-if="failedItems.length > 0" class="mt-2">
        <p class="text-xs text-status-error">ʧ败文件:</p>
        <ul class="text-xs text-status-error mt-1 space-y-0.5 max-h-24 overflow-y-auto">
          <li v-for="item in failedItems" :key="item.name">{{ item.name }}: {{ item.error }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  complete: boolean
  files: File[]
  successCount: number
  failedCount: number
  failedItems: { name: string; error?: string }[]
}>()

const resultTitle = computed(() => {
  if (props.failedCount === 0) return 'ȫ部上传成功'
  if (props.successCount === 0) return 'ȫ部上传失败'
  return '部分上传成功'
})

const resultClass = computed(() => {
  if (props.failedCount === 0) return 'bg-status-success/5 border-status-success/20'
  if (props.successCount === 0) return 'bg-status-error/5 border-status-error/20'
  return 'bg-status-warning/5 border-status-warning/20'
})

const iconClass = computed(() => {
  if (props.failedCount === 0) return 'pi pi-check-circle text-status-success'
  if (props.successCount === 0) return 'pi pi-times-circle text-status-error'
  return 'pi pi-exclamation-circle text-status-warning'
})
</script>
