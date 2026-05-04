<template>
  <Dialog
    :visible="visible"
    header="批量解析"
    :modal="true"
    :style="{ width: '450px' }"
    class="custom-dialog"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="py-4">
      <div class="flex items-start gap-4 mb-4">
        <div class="w-12 h-12 bg-gradient-to-br from-secondary/20 to-primary/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <i class="pi pi-play-circle text-secondary text-xl" />
        </div>
        <div>
          <p class="text-neutral-text font-medium mb-1">
            开始批量解析
          </p>
          <p class="text-neutral-text-secondary text-sm">
            确定要解析选中的 <span class="text-primary font-bold">{{ selectedLogs.length }}</span> 个日志文件吗？
          </p>
        </div>
      </div>
      <div
        v-if="selectedLogs.length > 0"
        class="space-y-2 max-h-40 overflow-y-auto bg-neutral-bg rounded-xl p-3"
      >
        <div
          v-for="log in selectedLogs"
          :key="log.id"
          class="flex items-center gap-2 p-2 bg-neutral-card rounded-lg"
        >
          <i class="pi pi-file text-primary" />
          <span class="text-sm text-neutral-text truncate">{{ log.fileName }}</span>
        </div>
      </div>
    </div>
    <template #footer>
      <Button
        label="取消"
        class="btn-ghost"
        @click="closeDialog"
      />
      <Button
        label="开始解析"
        icon="pi pi-play"
        class="btn-game"
        @click="startBatchParse"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 批量解析弹窗组件
 * 功能：处理批量解析日志文件
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

// Props
defineProps<{
  visible: boolean
  selectedLogs: Array<{
    id: string
    fileName: string
  }>
}>()

// Emits
const emit = defineEmits([
  'update:visible',
  'start-batch-parse'
])

// 事件处理
const closeDialog = () => {
  emit('update:visible', false)
}

const startBatchParse = () => {
  emit('start-batch-parse')
}
</script>