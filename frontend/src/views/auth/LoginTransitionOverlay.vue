<template>
  <transition name="fade">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/95 backdrop-blur-md">
      <div class="text-center animate-bounce-in">
        <div class="w-24 h-24 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30 animate-pulse">
          <span class="text-5xl">⚔️</span>
        </div>
        <h2 class="text-2xl font-bold text-white mb-2">登录成功</h2>
        <p class="text-gray-400">正在跳转至首ҳ...</p>
        <div class="mt-6 flex justify-center">
          <div class="w-64 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-blue-500 to-blue-700 rounded-full transition-all duration-1000 ease-out" :style="{ width: progress + '%' }" />
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
defineProps<{ show: boolean; progress: number }>()
</script>
