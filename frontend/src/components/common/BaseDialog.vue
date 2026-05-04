<template>
  <Dialog
    :visible="visible"
    :header="header"
    :modal="modal"
    :style="{ width }"
    class="custom-dialog"
    @update:visible="$emit('update:visible', $event)"
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
          @click="$emit('confirm')"
        />
      </slot>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * BaseDialog - 通用对话框基础组件
 * 功能：统一所有模块对话框的外壳、footer 布局和事件处理，减少重复模板代码
 * 作者：帅姐姐
 * 更新日期：2026-04-30
 */

import { computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

interface Props {
  visible: boolean
  header: string
  width?: string
  modal?: boolean
  showFooter?: boolean
  confirmLabel?: string
  confirmIcon?: string
  confirmSeverity?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning'
  cancelLabel?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '500px',
  modal: true,
  showFooter: true,
  confirmLabel: '确认',
  confirmIcon: '',
  confirmSeverity: 'primary',
  cancelLabel: '取消',
  loading: false
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
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
  emit('update:visible', false)
}
</script>
