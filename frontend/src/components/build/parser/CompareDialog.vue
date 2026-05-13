<template>
  <BaseDialog
    :visible="visible"
    header="添加对比Build"
    width="500px"
    :show-footer="false"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <FormField label="Build代码">
        <InputText
          v-model="compareCode"
          class="w-full"
          placeholder="粘贴Build代码"
        />
      </FormField>
      <BaseButton
        label="解析并添加"
        class="btn-game w-full"
        @click="addCompareBuild"
      />
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
/**
 * 添加对比Build弹窗组件
 * 功能：添加用于对比的Build
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref } from 'vue'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import FormField from '@/components/common/ui/input/FormField.vue'
import InputText from 'primevue/inputtext'

defineProps<{
  visible: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'add-compare-build': [code: string]
}>()

// 数据模型
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