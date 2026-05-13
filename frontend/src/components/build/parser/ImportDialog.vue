<template>
  <BaseDialog
    :visible="visible"
    header="导入Build代码"
    width="500px"
    confirm-label="导入"
    @update:visible="emit('update:visible', $event)"
    @confirm="importBuildCode"
  >
    <p class="text-sm text-neutral-text-secondary mb-4">
      支持导入以下格式：
    </p>
    <ul class="text-sm text-neutral-text-secondary mb-4 list-disc list-inside">
      <li>GW2原生的Build代码格ʽ（[&DQgBAAA=]）</li>
      <li>ARCDPS导出格ʽ</li>
      <li>DiscoGW2格ʽ</li>
    </ul>
    <Textarea
      v-model="importCode"
      rows="4"
      class="w-full"
      placeholder="粘贴Build代码..."
    />
  </BaseDialog>
</template>

<script setup lang="ts">
/**
 * 导入Build代码弹窗组件
 * 功能：导入不同格式的Build代码
 * 作者：帅姐姐姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import Textarea from 'primevue/textarea'

defineProps<{
  visible: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'import-build-code': [code: string]
}>()

// 数据模型
const importCode = ref('')

// 事件处理
const closeDialog = () => {
  emit('update:visible', false)
  importCode.value = ''
}

const importBuildCode = () => {
  emit('import-build-code', importCode.value)
  closeDialog()
}
</script>