<template>
  <div
    class="min-h-screen flex flex-col relative transition-colors duration-300"
    :class="{ 'theme-transition': isTransitioning }"
  >
    <!-- 主题背景动画层 -->
    <div
      class="fixed inset-0 pointer-events-none z-0 opacity-80 transition-opacity duration-300"
      :style="{
        background: 'radial-gradient(ellipse at 0% 0%, var(--color-primary-alpha-10) 0%, transparent 50%), radial-gradient(ellipse at 100% 100%, var(--color-ai-alpha-10) 0%, transparent 50%)'
      }"
    />

    <!-- 顶部导航栏 -->
    <TopNav />

    <!-- 主内容区域 -->
    <main class="flex-1 p-6 lg:p-8 overflow-x-hidden relative z-[1]">
      <router-view v-slot="{ Component }">
        <transition
          name="page"
          mode="out-in"
        >
          <component
            :is="Component"
            :key="$route.fullPath"
          />
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
let unsubscribe: (() => void) | null = null

onMounted(() => {
  unsubscribe = ThemeService.subscribe(() => {
    isTransitioning.value = true
    setTimeout(() => { isTransitioning.value = false }, 300)
  })
})

onUnmounted(() => {
  unsubscribe?.()
})
</script>

<style scoped>
/*
 * Vue <transition name="page"> 必需的 enter/leave 动画类。
 * 这些类名由 Vue 过渡系统自动生成，无法通过 Tailwind 工具类替代。
 */
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

.theme-transition {
  transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
