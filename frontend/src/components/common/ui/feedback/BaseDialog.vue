<template>
  <Dialog
    v-model:visible="visible"
    :header="header"
    :modal="modal"
    :style="{ width }"
    class="custom-dialog"
  >
    <slot />
    <template
      v-if="showFooter"
      #footer
    >
      <slot name="footer-actions">
        <Button
          :label="cancelLabel"
          class="btn-ghost"
          @click="close"
        />
        <Button
          :label="confirmLabel"
          :icon="confirmIcon"
          :class="confirmButtonClass"
          :loading="loading"
          :disabled="confirmDisabled"
          @click="$emit('confirm')"
        />
      </slot>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * BaseDialog - 通用对话框基础封装组件
 * 功能：对PrimeVue Dialog 的基础封装，用于项目中通用对话框的外壳和事件处理
 * 作者：帅姐姐 2026-04-30
 */

import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

interface Props {
  header: string
  width?: string
  modal?: boolean
  showFooter?: boolean
  confirmLabel?: string
  confirmIcon?: string
  confirmSeverity?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning'
  cancelLabel?: string
  loading?: boolean
  confirmDisabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '500px',
  modal: true,
  showFooter: true,
  confirmLabel: '确认',
  confirmIcon: '',
  confirmSeverity: 'primary',
  cancelLabel: '取消',
  loading: false,
  confirmDisabled: false
})

const visible = defineModel<boolean>('visible', { required: true })

const emit = defineEmits<{
  confirm: []
}>()

const confirmButtonClass = computed(() => {
  const map: Record<string, string> = {
    primary: 'btn-game',
    secondary: 'btn-secondary',
    success: 'btn-success',
    danger: 'btn-danger',
    warning: 'btn-warning'
  }
  return map[props.confirmSeverity] || 'btn-game'
})

const close = () => {
  visible.value = false
}
</script>
