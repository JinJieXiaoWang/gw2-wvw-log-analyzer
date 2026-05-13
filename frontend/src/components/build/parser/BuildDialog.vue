<template>
  <BaseDialog
    v-model:visible="visible"
    :header="isEditing ? '编辑Build' : '查看Build'"
    width="600px"
    :show-footer="false"
  >
    <p class="text-neutral-text-secondary">
      Build对话框功能开发中...
    </p>
  </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'

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
