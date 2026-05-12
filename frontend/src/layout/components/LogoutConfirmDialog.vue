<template>
  <BaseDialog
    v-model:visible="visible"
    header="确认退出登录"
    width="24rem"
    confirm-label="确认退出"
    confirm-severity="danger"
    :loading="isLoggingOut"
    @confirm="handleConfirm"
  >
    <div class="text-center py-4">
      <div
        class="w-16 h-16 bg-status-warning/10 rounded-full flex items-center
               justify-center mx-auto mb-4">
        <i class="pi pi-sign-out text-status-warning text-3xl" />
      </div>
      <p class="text-neutral-text-secondary">
        确定要退出当前账号吗？退出后将以游客身份浏览系统。
      </p>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
/**
 * 退出登录确认对话框
 * 功能：封装退出登录的确认交互
 */

import { defineModel } from 'vue'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'

const visible = defineModel<boolean>('visible', { default: false })

const props = defineProps<{
  isLoggingOut: boolean
}>()

const emit = defineEmits<{
  confirm: []
}>()

const handleConfirm = () => {
  emit('confirm')
}
</script>
