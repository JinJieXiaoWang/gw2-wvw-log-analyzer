<template>
  <div class="main-layout" :class="{ 'theme-transition': isTransitioning }">
    <!-- 主题背景动画层 -->
    <div class="theme-background" />
    
    <!-- 顶部导航栏 -->
    <TopNav />

    <!-- 主内容区域 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="$route.fullPath" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import TopNav from './components/topNav/index.vue'
import { ThemeService } from '@/services/system/themeService'

const isTransitioning = ref(false)

let unsubscribe: () => void

onMounted(() => {
  unsubscribe = ThemeService.subscribe(() => {
    isTransitioning.value = true
    setTimeout(() => {
      isTransitioning.value = false
    }, 300)
  })
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  position: relative;
  transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.theme-background {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background: 
    radial-gradient(ellipse at 0% 0%, var(--color-primary-alpha-10) 0%, transparent 50%),
    radial-gradient(ellipse at 100% 100%, var(--color-ai-alpha-10) 0%, transparent 50%);
  opacity: 0.8;
  transition: opacity 0.3s ease, background 0.3s ease;
}

.main-content {
  flex: 1;
  padding: 1.5rem;
  overflow-x: hidden;
  position: relative;
  z-index: 1;
}

@media (min-width: 1024px) {
  .main-content {
    padding: 2rem;
  }
}

/* 页面切换动画 */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 主题过渡状态 */
.theme-transition {
  transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>