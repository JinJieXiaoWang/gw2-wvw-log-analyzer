<template>
  <Dialog
    :visible="visible"
    header="导入循环对比"
    :modal="true"
    :style="{ width: '500px' }"
    @update:visible="emit('update:visible', $event)"
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

import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import Textarea from 'primevue/textarea'

// Props
const props = defineProps<{
  visible: boolean
}>()

// 确保props被使用
console.log(props.visible)

// Emits
const emit = defineEmits([
  'update:visible',
  'import-rotation'
])

// 状态
const idealRotationJson = ref('')
const actualRotationJson = ref('')

// 事件处理
const closeDialog = () => {
  emit('update:visible', false)
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