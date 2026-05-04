<template>
  <Dialog
    :visible="visible"
    header="导入Build代码"
    :modal="true"
    :style="{ width: '500px' }"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="py-4">
      <p class="text-sm text-neutral-text-secondary mb-4">
        支持以下格式：
      </p>
      <ul class="text-sm text-neutral-text-secondary mb-4 list-disc list-inside">
        <li>GW2原生的Build代码格式（[&DQgBAAA=]）</li>
        <li>ARCDPS导出格式</li>
        <li>DiscoGW2格式</li>
      </ul>
      <Textarea
        v-model="importCode"
        rows="4"
        class="w-full"
        placeholder="粘贴Build代码..."
      />
    </div>
    <template #footer>
      <Button
        label="取消"
        class="btn-ghost"
        @click="closeDialog"
      />
      <Button
        label="导入"
        class="btn-game"
        @click="importBuildCode"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 导入Build代码弹窗组件
 * 功能：导入不同格式的Build代码
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'

defineProps<{
  visible: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'import-build-code': [code: string]
}>()

// 状态
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