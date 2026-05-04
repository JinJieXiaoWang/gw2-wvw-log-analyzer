<template>
  <div
    class="card animate-slide-in-up"
    style="animation-delay: 0.1s"
  >
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
          <i class="pi pi-key text-primary" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-neutral-text">
            Build代码
          </h3>
          <p class="text-xs text-neutral-text-secondary">
            粘贴或导入你的Build代码
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          label="导入代码"
          icon="pi pi-upload"
          class="btn-ghost"
          size="small"
          @click="showImportDialog"
        />
        <Button
          label="粘贴"
          icon="pi pi-paste"
          class="btn-ghost"
          size="small"
          @click="pasteCode"
        />
        <Button
          label="清空"
          icon="pi pi-trash"
          class="btn-ghost"
          size="small"
          @click="clearCode"
        />
      </div>
    </div>
    <div class="relative">
      <Textarea
        v-model="localBuildCode"
        rows="6"
        class="w-full font-mono text-sm"
        placeholder="在此粘贴Build代码，例如：[&DQgBAAA=]..."
      />
      <div
        v-if="buildCode"
        class="absolute top-2 right-2"
      >
        <span class="game-badge game-badge-secondary">
          {{ buildCode.length }} 字符
        </span>
      </div>
    </div>
    <div class="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div class="flex gap-3">
        <Button
          label="解析代码"
          icon="pi pi-check"
          class="btn-game"
          :loading="isParsing"
          @click="parseBuildCode"
        />
        <Button
          label="从日志导入"
          icon="pi pi-file"
          class="btn-ghost"
          @click="showLogImportDialog"
        />
      </div>
      <div
        v-if="parseError"
        class="flex items-center gap-2 text-status-error"
      >
        <i class="pi pi-exclamation-circle" />
        <span class="text-sm">{{ parseError }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Build代码输入组件
 * 功能：处理Build代码的输入、解析和相关操作
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import { ref, watch } from 'vue'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'

// Props
const props = defineProps<{
  buildCode: string
  isParsing: boolean
  parseError: string
}>()

// Emits
const emit = defineEmits<{
  'update:buildCode': [value: string]
  'parse-build-code': []
  'show-import-dialog': []
  'show-log-import-dialog': []
  'clear-code': []
}>()

// 本地状态
const localBuildCode = ref(props.buildCode)

// 监听props变化
watch(() => props.buildCode, (newValue) => {
  localBuildCode.value = newValue
})

// 监听本地状态变化
watch(localBuildCode, (newValue) => {
  emit('update:buildCode', newValue)
})

// 事件处理
const showImportDialog = () => {
  emit('show-import-dialog')
}

const showLogImportDialog = () => {
  emit('show-log-import-dialog')
}

const parseBuildCode = () => {
  emit('parse-build-code')
}

const clearCode = () => {
  emit('clear-code')
}

const pasteCode = async () => {
  try {
    const text = await navigator.clipboard.readText()
    localBuildCode.value = text
  } catch (err) {
    console.error('Failed to read clipboard')
  }
}
</script>