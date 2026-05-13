<template>
  <Dialog
    :visible="visible"
    header="导入循环对比"
    :modal="true"
    :style="{ width: '500px' }"
    @update:visible="handleVisibleUpdate"
  >
    <div class="py-4">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-neutral-text-secondary mb-2">理想循环JSON</label>
          <Textarea
            v-model="idealRotationJson"
            rows="6"
            class="w-full"
            placeholder="粘贴理想循环数据..."
          />
        </div>
        <div>
          <label class="block text-sm text-neutral-text-secondary mb-2">实战循环JSON</label>
          <Textarea
            v-model="actualRotationJson"
            rows="6"
            class="w-full"
            placeholder="粘贴实战循环数据..."
          />
        </div>
      </div>
    </div>
    <template #footer>
      <BaseButton
        label="取消"
        variant="ghost"
        @click="closeDialog"
      />
      <BaseButton
        label="导入"
        variant="game"
        @click="importRotation"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 导入循环对比弹窗组件
 * 功能：处理导入循环对比数据
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import { ref } from 'vue'

const visible = defineModel<boolean>('visible')

const emit = defineEmits(['import-rotation'])

const idealRotationJson = ref('')
const actualRotationJson = ref('')

function handleVisibleUpdate(value: boolean) {
  visible.value = value
}

const closeDialog = () => {
  visible.value = false
  idealRotationJson.value = ''
  actualRotationJson.value = ''
}

const importRotation = () => {
  emit('import-rotation', {
    ideal: idealRotationJson.value,
    actual: actualRotationJson.value
  })
  closeDialog()
}
</script>