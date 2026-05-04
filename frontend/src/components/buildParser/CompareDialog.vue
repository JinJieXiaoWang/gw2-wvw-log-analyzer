<template>
  <Dialog
    :visible="visible"
    header="添加对比Build"
    :modal="true"
    :style="{ width: '500px' }"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="py-4">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-neutral-text-secondary mb-2">Build代码</label>
          <InputText
            v-model="compareCode"
            class="w-full"
            placeholder="粘贴Build代码"
          />
        </div>
        <Button
          label="解析并添加"
          class="btn-game w-full"
          @click="addCompareBuild"
        />
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 添加对比Build弹窗组件
 * 功能：添加用于对比的Build
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

defineProps<{
  visible: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'add-compare-build': [code: string]
}>()

// 状态
const compareCode = ref('')

// 事件处理
const addCompareBuild = () => {
  if (compareCode.value) {
    emit('add-compare-build', compareCode.value)
    emit('update:visible', false)
    compareCode.value = ''
  }
}
</script>