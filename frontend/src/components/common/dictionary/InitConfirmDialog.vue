<template>
  <BaseDialog
    v-model:visible="localVisible"
    header="初始化字典数据"
    width="450px"
    confirm-label="ȷ认初始化"
    confirm-severity="danger"
    :loading="initializing"
    @confirm="$emit('confirm')"
  >
    <div class="init-warning">
      <i class="pi pi-exclamation-triangle" />
      <div class="warning-content">
        <h4>ȷ认要初始化字典数据吗？</h4>
        <p>初始化操作将重置所有字典数据到系统默认ֵ。</p>
        <p class="warning-text">此操作不可恢复，请谨慎操作！</p>
      </div>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseDialog from '@/components/common/ui/BaseDialog.vue'

const props = defineProps<{
  visible: boolean
  initializing: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: []
}>()

const localVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
})
</script>

<style scoped>
.init-warning {
  display: flex; gap: 16px; padding: 16px;
  background: rgba(255, 125, 0, 0.1); border-radius: 8px; border: 1px solid #ff7d00;
}
.init-warning i { font-size: 32px; color: #ff7d00; }
.warning-content h4 { margin: 0 0 8px 0; color: #e5e5e5; }
.warning-content p { margin: 0; color: #909399; font-size: 14px; }
.warning-text { color: #ff7d00 !important; font-weight: 500; }
</style>
