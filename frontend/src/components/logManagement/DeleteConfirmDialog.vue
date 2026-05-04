<template>
  <Dialog
    :visible="visible"
    header="确认删除"
    :modal="true"
    :style="{ width: '450px' }"
    class="custom-dialog"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="py-4">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-status-error/10 rounded-xl flex items-center justify-center flex-shrink-0">
          <i class="pi pi-exclamation-triangle text-status-error text-xl" />
        </div>
        <div>
          <p class="text-neutral-text font-medium mb-1">
            确定要删除此日志吗？
          </p>
          <p class="text-sm text-neutral-text-secondary">
            此操作不可恢复，相关数据将永久删除。
          </p>
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
        label="删除"
        class="btn-danger"
        @click="deleteLog"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 删除确认弹窗组件
 * 功能：处理日志删除确认
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

// Props
defineProps<{
  visible: boolean
}>()

// Emits
const emit = defineEmits([
  'update:visible',
  'delete-log'
])

// 事件处理
const closeDialog = () => {
  emit('update:visible', false)
}

const deleteLog = () => {
  emit('delete-log')
  closeDialog()
}
</script>