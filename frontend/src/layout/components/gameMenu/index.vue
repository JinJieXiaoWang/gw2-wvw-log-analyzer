<template>
  <div class="relative">
    <!-- 菜单触发按钮 -->
    <button
      class="menu-trigger relative"
      :class="{ 'menu-active': isOpen }"
      @click="toggleMenu"
    >
      <div class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg shadow-primary/30 relative overflow-hidden group hover:scale-105 transition-transform">
        <!-- 菜单图标 -->
        <div
          class="flex flex-col gap-1.5 items-center transition-all duration-300"
          :class="{ 'opacity-0 -translate-y-2 scale-75': isOpen }"
        >
          <span class="w-5 h-0.5 bg-white rounded-full" />
          <span class="w-5 h-0.5 bg-white rounded-full" />
          <span class="w-4 h-0.5 bg-white rounded-full ml-auto mr-0.5" />
        </div>
        <!-- 关闭图标 -->
        <div
          class="absolute flex items-center justify-center transition-all duration-300"
          :class="{ 'opacity-100 scale-100': isOpen, 'opacity-0 scale-75': !isOpen }"
        >
          <i class="pi pi-times text-white text-lg" />
        </div>
      </div>
    </button>

    <!-- 游戏化菜单 -->
    <transition
      name="menu-dropdown"
      appear
    >
      <div
        v-if="isOpen"
        class="game-menu absolute top-full mt-3 right-0 z-50 min-w-[240px]"
        @click="closeMenu"
      >
        <div class="bg-neutral-card border border-neutral-border rounded-xl shadow-2xl shadow-neutral-shadow/50 overflow-hidden">
          <!-- 装饰性头部 -->
          <div class="px-4 py-3 border-b border-neutral-border bg-gradient-to-r from-primary/10 via-secondary/5 to-transparent">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-secondary animate-pulse" />
              <span class="text-sm font-bold text-neutral-text">导航面板</span>
            </div>
          </div>

          <!-- 菜单列表 -->
          <div class="p-2">
            <router-link
              v-for="(item, index) in menuItems"
              :key="item.path"
              :to="item.path"
              class="menu-item group flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200"
              :class="{ 'menu-item-active': isActive(item.path) }"
              :style="{ animationDelay: `${index * 30}ms` }"
            >
              <div
                class="menu-icon w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 shadow-sm"
                :class="isActive(item.path) ? 'bg-gradient-to-br from-primary to-secondary text-white shadow-lg shadow-primary/30' : 'bg-neutral-bg text-neutral-text-secondary group-hover:bg-primary/10 group-hover:text-primary'"
              >
                <i :class="item.icon" />
              </div>
              <div class="flex-1">
                <span
                  class="text-sm font-semibold transition-colors duration-200 block"
                  :class="isActive(item.path) ? 'text-primary' : 'text-neutral-text group-hover:text-primary'"
                >
                  {{ item.label }}
                </span>
                <span
                  v-if="item.description"
                  class="text-xs text-neutral-text-disabled mt-0.5 block"
                >
                  {{ item.description }}
                </span>
              </div>
              <i
                v-if="isActive(item.path)"
                class="pi pi-check-circle text-primary text-lg"
              />
            </router-link>
          </div>

          <!-- 装饰性底部 -->
          <div class="px-4 py-3 border-t border-neutral-border bg-gradient-to-r from-transparent via-neutral-bg/50 to-transparent">
            <div class="flex items-center justify-between">
              <span class="text-xs text-neutral-text-disabled font-medium">
                GW2 WVW 日志系统
              </span>
              <div class="flex gap-1">
                <div class="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-secondary animate-pulse" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
/**
 * GameMenu - 游戏化导航菜单组件
 * 功能：提供符合游戏UI风格的页面导航
 * 设计：使用渐变、阴影、动画等游戏化元素
 */

import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePermission } from '@/composables/system/usePermission'

const route = useRoute()
const isOpen = ref(false)
const { isAuthenticated, can } = usePermission()

interface MenuItem {
  path: string
  label: string
  icon: string
  description?: string
  requireAuth?: boolean
  permissions?: string[]
  hidden?: boolean
}

const allMenuItems: MenuItem[] = [
  {
    path: '/',
    label: '数据看板',
    icon: 'pi pi-chart-line',
    description: '可视化数据'
  },
  {
    path: '/logs',
    label: '日志管理',
    icon: 'pi pi-file',
    description: '解析与管理'
  },
  {
    path: '/attendance',
    label: '出勤统计',
    icon: 'pi pi-users',
    description: '团队数据'
  },
  {
    path: '/skill-analysis',
    label: '技能循环',
    icon: 'pi pi-sync',
    description: '循环分析'
  },
  {
    path: '/build-parser',
    label: 'Build解析',
    icon: 'pi pi-code',
    description: '配置分析'
  },
  {
    path: '/builds',
    label: '配置图书馆',
    icon: 'pi pi-book',
    description: '战场配置百科'
  },
  {
    path: '/settings',
    label: '设置',
    icon: 'pi pi-cog',
    description: '系统配置',
    requireAuth: true,
    permissions: ['write']
  }
]

const menuItems = computed(() => {
  return allMenuItems.filter(item => {
    if (item.hidden) {
      return false
    }
    if (item.requireAuth && !isAuthenticated.value) {
      return false
    }
    if (item.permissions && item.permissions.length > 0) {
      return item.permissions.some(p => can(p as any))
    }
    return true
  })
})

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const closeMenu = () => {
  isOpen.value = false
}

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/' || route.path === '/dashboard'
  }
  return route.path.startsWith(path)
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>


