<template>
  <Dialog
    v-model:visible="visible"
    :header="isEditing ? '编辑Build' : '查看Build'"
    :style="{ width: '600px' }"
    :modal="true"
  >
    <div class="p-4">
      <p class="text-neutral-text-secondary">
        Build对话框功能开发中...
      </p>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'

const visible = defineModel<boolean>('visible', { default: false })

defineProps<{
  build?: any
  isEditing?: boolean
}>()

defineEmits<{
  save: [data: any]
  delete: [buildId: string]
}>()
</script>
