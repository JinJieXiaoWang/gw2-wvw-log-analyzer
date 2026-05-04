<template>
  <div class="welcome-banner animate-slide-in-up">
    <div class="welcome-banner-content">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg float-element">
            <i class="pi pi-code text-3xl text-white" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-neutral-text mb-1">
              Build代码解析
            </h1>
            <p class="text-neutral-text-secondary text-sm">
              导入、解析和对比GW2 Build代码
            </p>
          </div>
        </div>
        <div class="flex gap-3">
          <Button
            label="保存Build"
            icon="pi pi-save"
            class="btn-game"
            severity="secondary"
            @click="showSaveDialog"
          />
          <Button
            label="分享Build"
            icon="pi pi-share"
            class="btn-game"
            @click="shareBuild"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Build代码解析页面欢迎横幅组件
 * 功能：显示页面标题和操作按钮
 * 作者：帅姐姐
 * 创建日期：2026-04-27
 */

import Button from 'primevue/button'

// Emits
const emit = defineEmits<{
  'show-save-dialog': []
  'share-build': []
}>()

// 事件处理
const showSaveDialog = () => {
  emit('show-save-dialog')
}

const shareBuild = () => {
  emit('share-build')
}
</script>