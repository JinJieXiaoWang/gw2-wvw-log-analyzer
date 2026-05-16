<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="bg-neutral-card rounded-2xl p-8 border border-neutral-border shadow-2xl max-w-md w-full mx-4 animate-scale-in">
      <div class="text-center">
        <div class="relative w-20 h-20 mx-auto mb-6">
          <div class="absolute inset-0 bg-gradient-to-br from-primary to-purple-600 rounded-full animate-pulse opacity-50" />
          <div class="absolute inset-2 bg-neutral-card rounded-full flex items-center justify-center">
            <div class="w-10 h-10 border-4 border-ai border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
        <h3 class="text-xl font-bold text-white mb-2">{{ title }}</h3>
        <p class="text-neutral-text-secondary mb-6">{{ message }}</p>
        <div class="w-full bg-neutral-card-active rounded-full h-2 overflow-hidden">
          <!-- 动态值，无法使用 Tailwind 静态类 -->
          <div class="bg-gradient-to-r from-ai via-primary to-purple-500 h-2 rounded-full transition-all duration-500" :style="{ width: progress + '%' }" />
        </div>
        <p class="text-xs text-neutral-text-tertiary mt-2">{{ progress.toFixed(0) }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; message: string; progress: number }>()
</script>

<style scoped>
.animate-scale-in { animation: scaleIn 0.3s ease-out; }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>
