<template>
  <div class="welcome-banner animate-slide-in-up">
    <div class="welcome-banner-content">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center shadow-lg shadow-primary/30 float-element">
            <i class="pi pi-database text-3xl text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-neutral-text mb-1">
              战斗日志管理
            </h1>
            <p class="text-neutral-text-secondary text-sm">
              记录每一场荣耀之战，解析战场数据
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <Button
            v-permission="'admin'"
            label="上传日志"
            icon="pi pi-upload"
            class="btn-game"
            @click="showUploadDialog"
          />
           <Button
            v-permission="'admin'"
            label="批量解析"
            icon="pi pi-play"
            class="btn-game"
            severity="secondary"
            :disabled="selectedLogs.length === 0"
            @click="showBatchParseDialog"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 日志管理页面欢迎横幅组件
 * 功能：展示页面标题和操作按钮
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Button from 'primevue/button'

// Props
defineProps<{
  selectedLogs: any[]
}>()

// Emits
const emit = defineEmits<{
  'show-upload-dialog': []
  'show-batch-parse-dialog': []
}>()

// 事件处理
const showUploadDialog = () => {
  emit('show-upload-dialog')
}

const showBatchParseDialog = () => {
  emit('show-batch-parse-dialog')
}
</script>