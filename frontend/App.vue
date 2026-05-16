<template>
  <div
    id="app"
    class="min-h-screen bg-neutral-bg"
  >
    <!-- 数据加载中 -->
    <div
      v-if="!isDataReady"
      class="fixed inset-0 bg-neutral-bg flex items-center justify-center z-[200]"
    >
      <div class="text-center">
        <div class="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto mb-4" />
        <p class="text-neutral-text-secondary">
          正在加载职业数据...
        </p>
      </div>
    </div>
    
    <!-- 服务状态警告 -->
    <ServiceStatusWarning />
    
    <router-view v-slot="{ Component, route }">
      <transition
        name="page"
        mode="out-in"
      >
        <component
          :is="Component"
          :key="route.path"
        />
      </transition>
    </router-view>
    
    <!-- 全局页面水印 -->
    <AppWatermark />

    <!-- 页面加载进度条 -->
    <transition name="fade">
      <div
        v-if="isLoading"
        class="fixed top-0 left-0 right-0 h-1 z-[100] bg-neutral-border"
      >
        <div
          class="h-full bg-gradient-to-r from-primary via-secondary to-primary animate-progress"
        />
      </div>
    </transition>

    <!-- 全局 Toast（用于认证事件等全局提示） -->
    <Toast position="top-right" />
  </div>
</template>

<script setup lang="ts">
/**
 * App.vue - 应用根组件
 * 功能：全局布局、页面过渡、全局提示
 * 优化：2026-05-11 - 优化页面过渡动画时间，提升响应速度
 * 优化：2026-05-12 - 添加职业数据预加载，确保页面渲染时数据已就绪
 */

import ServiceStatusWarning from '@/components/common/ServiceStatusWarning.vue'
import AppWatermark from '@/components/system/AppWatermark.vue'
import { useSettingsStore } from '@/store/system/settings'
import { initProfessionData } from '@/utils/profession/professionUtils'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { onMounted, onUnmounted, ref } from 'vue'

const isLoading = ref(false)
const isDataReady = ref(false)
const settingsStore = useSettingsStore()
const toast = useToast()

/**
 * 全局 Toast 事件处理
 * 供 main.ts 等非 Vue 组件场景调用
 */
const handleGlobalToast = (event: Event) => {
  const detail = (event as CustomEvent).detail
  if (detail) {
    toast.add({
      severity: detail.severity || 'info',
      summary: detail.summary || '提示',
      detail: detail.message || detail.detail || '',
      life: detail.life || 3000
    })
  }
}

/**
 * 预加载职业数据
 */
async function preloadProfessionData(): Promise<void> {
  try {
    await initProfessionData()
    isDataReady.value = true
  } catch (error) {
    console.error('[App] 职业数据预加载失败:', error)
    // 即使加载失败也继续显示页面
    isDataReady.value = true
  }
}

onMounted(async () => {
  // 预加载职业数据（在渲染页面之前）
  await preloadProfessionData()

  // 从后端同步全局设置（水印等策略配置）
  settingsStore.syncFromServer()

  // 使用setTimeout确保DOM已渲染
  setTimeout(() => {
    const event = new Event('pageTransitionStart')
    window.dispatchEvent(event)
  }, 100)

  // 监听全局 Toast 事件
  window.addEventListener('global:toast', handleGlobalToast)
})

onUnmounted(() => {
  window.removeEventListener('global:toast', handleGlobalToast)
})
</script>

<style>
#app {
  min-height: 100vh;
}

/**
 * 页面过渡动画
 * 优化：减少过渡时间，提升页面切换响应速度
 */
.page-enter-active {
  transition: all 0.25s ease-out;
}

.page-leave-active {
  transition: all 0.2s ease-in;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.99);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-5px) scale(0.99);
}

/* 进度条动画 */
.animate-progress {
  animation: progressMove 1s ease-in-out infinite;
}

@keyframes progressMove {
  0% {
    width: 0%;
    margin-left: 0%;
  }
  50% {
    width: 60%;
    margin-left: 20%;
  }
  100% {
    width: 0%;
    margin-left: 100%;
  }
}

/* 淡入淡出过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 无障碍：减少动画 */
@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active {
    transition: none;
  }
  
  .page-enter-from,
  .page-leave-to {
    opacity: 1;
    transform: none;
  }
  
  .animate-progress {
    animation: none;
    width: 50%;
  }
}
</style>
