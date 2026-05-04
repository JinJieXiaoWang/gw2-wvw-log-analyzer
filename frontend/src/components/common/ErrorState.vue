<template>
  <div class="flex flex-col items-center justify-center py-10 px-4 text-center gap-3">
    <div class="text-5xl text-status-error mb-2">
      <i class="pi pi-exclamation-triangle" />
    </div>
    <h3 class="text-neutral-text text-lg font-semibold m-0">
      {{ title }}
    </h3>
    <p class="text-neutral-text-secondary text-sm max-w-xs m-0">
      {{ message }}
    </p>
    <div class="flex items-center justify-center gap-3 mt-4 flex-wrap">
      <Button 
        v-if="showRetry" 
        :label="retryText" 
        class="btn-game"
        @click="$emit('retry')"
      />
      <Button 
        v-if="showHome" 
        :label="homeText" 
        class="btn-game"
        outlined
        @click="$emit('home')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 错误状态组件
 * 功能：展示错误信息并提供重试/返回等操作
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import Button from 'primevue/button'

interface Props {
  title?: string
  message?: string
  showRetry?: boolean
  showHome?: boolean
  retryText?: string
  homeText?: string
}

withDefaults(defineProps<Props>(), {
  title: '加载失败',
  message: '发生错误，请稍后重试',
  showRetry: true,
  showHome: true,
  retryText: '重试',
  homeText: '返回首页'
})

defineEmits(['retry', 'home'])
</script>
