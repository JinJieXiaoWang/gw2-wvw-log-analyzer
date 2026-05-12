<template>
  <Dialog
    v-bind="$attrs"
    :visible="visible"
    :header="header"
    :modal="modal"
    :style="{ width }"
    :pt="dialogPt"
    @update:visible="$emit('update:visible', $event)"
  >
    <slot />
    <template
      v-if="showFooter"
      #footer
    >
      <slot name="footer-actions">
        <BaseButton
          :label="cancelLabel"
          severity="secondary"
          variant="text"
          @click="close"
        />
        <BaseButton
          :label="confirmLabel"
          :icon="confirmIcon"
          :severity="confirmSeverity"
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
 * 功能：对 PrimeVue Dialog 的基础封装，提供统一的对话框外壳、底部操作栏和事件处理
 * 作者：帅姐姐 2026-04-30
 * 更新：2026-05-12 - 添加 v-bind="$attrs" 透传 PrimeVue Dialog 原生 props；
 *       取消按钮改用 severity + variant 标准 API；确认按钮 severity 类型对齐 PrimeVue v4
 */

import Dialog from 'primevue/dialog'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

interface Props {
  visible: boolean
  header: string
  width?: string
  modal?: boolean
  showFooter?: boolean
  confirmLabel?: string
  confirmIcon?: string
  confirmSeverity?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'contrast'
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

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: []
}>()

const close = () => {
  emit('update:visible', false)
}

// 通过 PT 传递自定义类名，遵循 PrimeVue v4 规范
const dialogPt = {
  root: {
    class: 'custom-dialog'
  }
}
</script>
