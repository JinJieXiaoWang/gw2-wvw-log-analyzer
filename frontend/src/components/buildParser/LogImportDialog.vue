<template>
  <Dialog
    :visible="visible"
    header="从日志导入"
    :modal="true"
    :style="{ width: '500px' }"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="py-4">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-neutral-text-secondary mb-2">选择日志</label>
          <Dropdown
            v-model="selectedLogId"
            :options="logOptions"
            option-label="label"
            option-value="value"
            placeholder="选择日志"
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm text-neutral-text-secondary mb-2">选择玩家</label>
          <Dropdown
            v-model="selectedPlayerName"
            :options="playerOptions"
            option-label="label"
            option-value="value"
            placeholder="选择玩家"
            class="w-full"
          />
        </div>
      </div>
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
        @click="importFromLog"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 从日志导入Build弹窗组件
 * 功能：从战斗日志中导入Build代码
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'

defineProps<{
  visible: boolean
  logOptions: any[]
  playerOptions: any[]
}>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'import-from-log': [logId: string | null, playerName: string | null]
}>()

// 状态
const selectedLogId = ref<string | null>(null)
const selectedPlayerName = ref<string | null>(null)

// 事件处理
const closeDialog = () => {
  emit('update:visible', false)
  selectedLogId.value = null
  selectedPlayerName.value = null
}

const importFromLog = () => {
  emit('import-from-log', selectedLogId.value, selectedPlayerName.value)
  closeDialog()
}
</script>