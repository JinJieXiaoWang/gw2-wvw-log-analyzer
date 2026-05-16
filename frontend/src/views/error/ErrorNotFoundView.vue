<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh]">
    <div class="w-24 h-24 bg-neutral-card rounded-full flex items-center justify-center mb-6">
      <span class="text-6xl font-bold text-neutral-text-disabled">404</span>
    </div>
    <h3 class="text-2xl font-semibold text-neutral-text mb-2">
      页面未找到
    </h3>
    <p class="text-neutral-text-secondary text-center mb-6">
      抱歉，您访问的页面不存在或已被移除
    </p>
    <div class="flex gap-3">
      <BaseButton
        label="返回首页"
        icon="pi pi-home"
        @click="goHome"
      />
      <BaseButton
        label="返回上一页"
        variant="secondary"
        icon="pi pi-arrow-left"
        @click="goBack"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

const router = useRouter()

const goHome = () => {
  router.push('/home')
}

const goBack = () => {
  router.back()
}
</script>
