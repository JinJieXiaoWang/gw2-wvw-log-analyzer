<template>
  <BaseDialog
    :visible="visible"
    header="从日志导入Build"
    :modal="
      true"
    :style="{ width: '500px' }"
    confirm-label="导入"
    @confirm="importFromLog"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <div>
        <FormField label="选择日志">
          <BaseSelect
            v-model="selectedLogId"
            :options="logOptions"
            option-label="label"
            option-value="value"
            placeholder="选择日志"
            class="w-full"
          />
        </FormField>
      </div>
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">选择玩家</label>
        <BaseSelect
          v-model="selectedPlayerName"
          :options="playerOptions"
          option-label="label"
          option-value="value"
          placeholder="选择玩家"
          class="w-full"
        />
      </div>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
/**
 * 从日志导入Build弹窗组件
 * 功能：从战斗日志中导入Build配置
 * 作者：帅姐姐
 * 日期：2026-04-27
 */

import { ref } from 'vue'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import FormField from '@/components/common/ui/input/FormField.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'

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

// 状态管理
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