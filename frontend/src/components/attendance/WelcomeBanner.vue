<template>
  <div class="welcome-banner animate-slide-in-up">
    <div class="welcome-banner-content">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-status-success to-primary flex items-center justify-center shadow-lg float-element">
            <i class="pi pi-users text-3xl text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-neutral-text mb-1">
              出勤统计
            </h1>
            <p class="text-neutral-text-secondary text-sm">
              查看团队和个人的战斗出勤数据
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <Button
            label="评分规则"
            icon="pi pi-chart-line"
            class="btn-ghost"
            size="small"
            @click="emit('view-scoring-rules')"
          />
          <Button
            label="导出Excel"
            icon="pi pi-file-excel"
            class="btn-game"
            severity="secondary"
            @click="exportExcel"
          />
          <Button
            label="导出CSV"
            icon="pi pi-file-pdf"
            class="btn-game"
            @click="exportCSV"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 出勤统计页面欢迎横幅组件
 * 功能：显示页面标题和操作按钮
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Button from 'primevue/button'

// Emits
const emit = defineEmits<{
  'export-excel': []
  'export-csv': []
  'view-scoring-rules': []
}>()

// 事件处理
const exportExcel = () => {
  emit('export-excel')
}

const exportCSV = () => {
  emit('export-csv')
}
</script>