<template>
  <div class="welcome-banner animate-slide-in-up">
    <div class="welcome-banner-content">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-secondary to-status-warning flex items-center justify-center shadow-lg float-element">
            <i class="pi pi-sync text-3xl text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-neutral-text mb-1">
              技能循环分析
            </h1>
            <p class="text-neutral-text-secondary text-sm">
              对比理想循环与实战循环，优化技能释放顺序
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <BaseButton
            label="导入对比"
            icon="pi pi-upload"
            variant="secondary"
            @click="showImportDialog"
          />
          <BaseButton
            label="导出报告"
            icon="pi pi-download"
            variant="game"
            @click="exportReport"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 技能循环分析页面欢迎横幅组件
 * 功能：展示页面标题和操作按钮
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'

// Emits
const emit = defineEmits([
  'show-import-dialog',
  'export-report'
])

// 事件处理
const showImportDialog = () => {
  emit('show-import-dialog')
}

const exportReport = () => {
  emit('export-report')
}
</script>