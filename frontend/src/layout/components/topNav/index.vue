<template>
  <header class="h-16 backdrop-blur-md border-b flex items-center justify-between px-4 lg:px-6 flex-shrink-0 sticky top-0 z-50 transition-all duration-300"
    :style="{ 
      backgroundColor: 'var(--color-card)',
      borderColor: 'var(--color-border)',
      boxShadow: '0 1px 3px var(--color-shadow)'
    }">
    <div class="flex items-center gap-6">
      <!-- Logo区域 -->
      <router-link
        to="/"
        class="flex items-center gap-3 group"
      >
        <div class="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg shadow-primary/30 relative overflow-hidden group-hover:scale-105 transition-transform bg-neutral-card">
          <img src="@/assets/fonts/logo.png" alt="GW2 Logo" class="w-10 h-10 object-contain" />
          <div class="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        <div class="hidden sm:block">
          <h1 class="text-neutral-text font-bold text-base leading-tight">
            WVW日志分析
          </h1>
          <p class="text-neutral-text-disabled text-sm">
            战场战斗记录解析
          </p>
        </div>
      </router-link>

      <!-- 主导航菜单 -->
      <nav class="hidden lg:flex items-center gap-1">
        <router-link
          v-for="item in visibleMenuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item group relative px-4 py-2 rounded-lg transition-all duration-200 flex items-center gap-2"
          :class="{ 'nav-item-active': isActive(item.path) }"
        >
          <i :class="item.icon" />
          <span class="text-base font-medium">{{ item.label }}</span>

          <!-- 悬停下划线动画 -->
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-300 group-hover:w-3/4" />

          <!-- 激活状态指示器 -->
          <div
            v-if="isActive(item.path)"
            class="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-0.5 bg-gradient-to-r from-primary to-secondary rounded-full"
          />
        </router-link>
      </nav>
    </div>

    <!-- 右侧功能区 -->
    <div class="flex items-center gap-2 sm:gap-3">
      <!-- 搜索框（桌面端） -->
      <div class="hidden xl:flex items-center">
        <div class="relative group">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索日志、玩家..."
            class="w-72 pl-11 pr-12 py-2.5 bg-neutral-bg/50 border border-neutral-border rounded-xl text-base text-neutral-text placeholder-neutral-text-disabled focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all group-hover:bg-neutral-bg"
            @keyup.enter="handleSearch"
          >
          <i class="pi pi-search absolute left-4 top-1/2 -translate-y-1/2 text-neutral-text-disabled group-hover:text-primary transition-colors" />
          <kbd class="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-1 bg-neutral-bg border border-neutral-border rounded text-xs text-neutral-text-disabled hidden group-hover:flex items-center gap-1">
            <span>⌘</span><span>K</span>
          </kbd>
        </div>
      </div>

      <!-- 主题切换器 -->
      <ThemeSwitcher />

      <!-- 快捷搜索按钮（移动端） -->
      <button class="xl:hidden p-2.5 hover:bg-neutral-bg rounded-xl transition-colors">
        <i class="pi pi-search text-neutral-text-secondary text-lg" />
      </button>

      <!-- 移动端菜单按钮 -->
      <button
        class="lg:hidden p-2.5 hover:bg-neutral-bg rounded-xl transition-colors"
        @click="toggleMobileMenu"
      >
        <i
          :class="mobileMenuOpen ? 'pi pi-times' : 'pi pi-bars'"
          class="text-neutral-text-secondary text-lg"
        />
      </button>

      <!-- 通知按钮（仅操作员可见） -->
      <div
        v-if="isOperator"
        class="relative"
      >
        <button
          class="relative p-2.5 hover:bg-neutral-bg rounded-xl transition-all hover:scale-105 group notification-btn"
          @click="toggleNotifications"
        >
          <i class="pi pi-bell text-neutral-text-secondary group-hover:text-primary transition-colors text-xl" />
          <span
            v-if="unreadCount > 0"
            class="absolute -top-1 -right-1 min-w-[20px] h-5 bg-gradient-to-r from-status-error to-secondary text-white text-xs font-bold rounded-full flex items-center justify-center px-1.5 shadow-lg animate-pulse"
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </button>

        <!-- 通知下拉菜单 -->
        <transition
          name="dropdown"
          appear
        >
          <div
            v-if="showNotifications"
            class="notification-dropdown absolute top-full mt-2 right-0 w-80 sm:w-96 bg-neutral-card border border-neutral-border rounded-xl shadow-2xl shadow-neutral-shadow/50 overflow-hidden z-50"
          >
            <div class="px-4 py-3 border-b border-neutral-border bg-gradient-to-r from-primary/5 to-secondary/5 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary animate-pulse" />
                <span class="text-base font-bold text-neutral-text">通知中心</span>
              </div>
              <button
                v-if="unreadCount > 0"
                class="text-sm text-primary hover:text-primary/80 transition-colors"
                @click.stop="markAllAsRead"
              >
                全部已读
              </button>
            </div>
            <div class="max-h-80 overflow-y-auto">
              <div
                v-for="notification in notifications"
                :key="notification.id"
                class="px-4 py-3 hover:bg-neutral-bg/50 border-b border-neutral-border/50 last:border-b-0 transition-colors cursor-pointer"
                :class="{ 'bg-primary/5': !notification.read }"
                @click.stop="handleNotificationClick(notification)"
              >
                <div class="flex items-start gap-3">
                  <div
                    class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    :class="getNotificationIconClass(notification.type)"
                  >
                    <i :class="getNotificationIcon(notification.type)" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-base font-medium text-neutral-text mb-0.5">
                      {{ notification.title }}
                    </p>
                    <p class="text-sm text-neutral-text-secondary line-clamp-2">
                      {{ notification.message }}
                    </p>
                    <p class="text-xs text-neutral-text-disabled mt-1">
                      {{ notification.time }}
                    </p>
                  </div>
                  <div
                    v-if="!notification.read"
                    class="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-2"
                  />
                </div>
              </div>
              <div
                v-if="notifications.length === 0"
                class="py-12 text-center"
              >
                <i class="pi pi-bell-slash text-4xl text-neutral-text-disabled mb-2" />
                <p class="text-base text-neutral-text-secondary">
                  暂无通知
                </p>
              </div>
            </div>
            <div class="px-4 py-2 border-t border-neutral-border bg-neutral-bg/50 text-center">
              <button class="text-base text-primary hover:text-primary/80 transition-colors">
                查看全部通知
              </button>
            </div>
          </div>
        </transition>
      </div>

      <!-- 用户信息区域 -->
      <div class="relative">
        <button
          class="flex items-center gap-2 p-1.5 pr-3 hover:bg-neutral-bg rounded-xl transition-all hover:scale-[1.02] user-menu-trigger"
          @click="toggleUserMenu"
        >
          <!-- 用户头像 -->
          <div class="relative">
            <div class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-md shadow-primary/20 overflow-hidden ring-2 ring-primary/20">
              <span class="text-white font-bold text-base">{{ userInitial }}</span>
            </div>
            <div class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-status-success rounded-full border-2 border-neutral-card" />
          </div>
          <!-- 用户信息（桌面端） -->
          <div class="hidden sm:block text-left">
            <p class="text-base font-semibold text-neutral-text leading-tight">
              {{ isAuthenticated ? (user?.username || '操作员') : '游客' }}
            </p>
            <div class="flex items-center gap-1">
              <span
                :class="isAuthenticated ? 'text-primary' : 'text-neutral-text-disabled'"
                class="text-sm"
              >
                {{ isAuthenticated ? '操作员' : '浏览模式' }}
              </span>
            </div>
          </div>
          <i class="pi pi-chevron-down text-sm text-neutral-text-disabled hidden sm:block" />
        </button>

        <!-- 用户下拉菜单 -->
        <transition
          name="dropdown"
          appear
        >
          <div
            v-if="showUserMenu"
            class="user-dropdown absolute top-full mt-2 right-0 w-64 bg-neutral-card border border-neutral-border rounded-xl shadow-2xl shadow-neutral-shadow/50 overflow-hidden z-50"
          >
            <!-- 已登录状态（操作员） -->
            <div v-if="isAuthenticated">
              <div class="px-4 py-3 border-b border-neutral-border bg-gradient-to-r from-primary/5 to-secondary/5">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-white font-bold text-lg">{{ userInitial }}</span>
                  </div>
                  <div>
                    <p class="text-base font-bold text-neutral-text">
                      {{ user?.username }}
                    </p>
                    <p class="text-sm text-neutral-text-secondary">
                      系统操作员
                    </p>
                  </div>
                </div>
              </div>
              <div class="p-2">
                <!-- 设置页面（仅操作员可见） -->
                <router-link
                  v-if="can('write')"
                  to="/settings"
                  class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-neutral-bg transition-colors group"
                  @click="closeUserMenu"
                >
                  <div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <i class="pi pi-cog text-primary text-base" />
                  </div>
                  <div>
                    <p class="text-base font-medium text-neutral-text">
                      系统设置
                    </p>
                    <p class="text-sm text-neutral-text-disabled">
                      配置管理
                    </p>
                  </div>
                </router-link>
                <!-- 管理员后台（仅操作员可见） -->
                <router-link
                  v-if="can('write')"
                  to="/admin"
                  class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-neutral-bg transition-colors group"
                  @click="closeUserMenu"
                >
                  <div class="w-8 h-8 bg-secondary/10 rounded-lg flex items-center justify-center group-hover:bg-secondary/20 transition-colors">
                    <i class="pi pi-shield text-secondary text-base" />
                  </div>
                  <div>
                    <p class="text-base font-medium text-neutral-text">
                      管理员后台
                    </p>
                    <p class="text-sm text-neutral-text-disabled">
                      高级管理
                    </p>
                  </div>
                </router-link>
              </div>
              <div class="px-4 py-3 border-t border-neutral-border bg-neutral-bg/50">
                <button
                  class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-status-error/10 to-status-error/5 hover:from-status-error/20 hover:to-status-error/10 text-status-error rounded-lg transition-all group logout-btn"
                  @click="showLogoutConfirmDialog = true"
                >
                  <i class="pi pi-sign-out group-hover:translate-x-0.5 transition-transform" />
                  <span class="text-base font-medium">退出登录</span>
                </button>
              </div>
            </div>

            <!-- 未登录状态（游客） -->
            <div v-else>
              <div class="px-4 py-6 text-center border-b border-neutral-border">
                <div class="w-16 h-16 bg-neutral-bg rounded-full flex items-center justify-center mx-auto mb-3">
                  <i class="pi pi-user text-3xl text-neutral-text-disabled" />
                </div>
                <p class="text-base text-neutral-text-secondary mb-4">
                  登录后可上传日志和管理系统
                </p>
                <router-link
                  to="/login"
                  class="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-primary to-secondary text-white rounded-lg hover:opacity-90 transition-opacity shadow-lg shadow-primary/30"
                  @click="closeUserMenu"
                >
                  <i class="pi pi-sign-in" />
                  <span class="text-base font-medium">操作员登录</span>
                </router-link>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </header>

  <!-- 退出登录确认对话框 -->
  <transition name="fade">
    <div
      v-if="showLogoutConfirmDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      @click.self="showLogoutConfirmDialog = false"
    >
      <div class="bg-neutral-card border border-neutral-border rounded-2xl p-6 w-full max-w-md mx-4 animate-scale-in">
        <div class="text-center">
          <div class="w-16 h-16 bg-status-warning/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="pi pi-sign-out text-status-warning text-3xl" />
          </div>
          <h3 class="text-xl font-bold text-neutral-text mb-2">确认退出登录</h3>
          <p class="text-neutral-text-secondary mb-6">
            确定要退出当前账号吗？退出后将以游客身份浏览系统。
          </p>
          <div class="flex gap-3">
            <button
              class="flex-1 px-4 py-3 bg-neutral-bg hover:bg-neutral-bg/80 text-neutral-text rounded-xl transition-all font-medium"
              @click="showLogoutConfirmDialog = false"
            >
              取消
            </button>
            <button
              class="flex-1 px-4 py-3 bg-gradient-to-r from-status-error to-status-error/80 hover:from-status-error/90 hover:to-status-error/70 text-white rounded-xl transition-all font-medium flex items-center justify-center gap-2 logout-confirm-btn"
              :disabled="isLoggingOut"
              @click="handleLogout"
            >
              <svg
                v-if="isLoggingOut"
                class="animate-spin h-5 w-5"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                  fill="none"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span>{{ isLoggingOut ? '退出中...' : '确认退出' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>

  <!-- 移动端全屏菜单 -->
  <transition
    name="mobile-menu"
    appear
  >
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-neutral-bg/95 backdrop-blur-md z-40 lg:hidden pt-20 px-4"
      @click="toggleMobileMenu"
    >
      <div
        class="bg-neutral-card border border-neutral-border rounded-2xl p-4 space-y-2"
        @click.stop
      >
        <router-link
          v-for="item in visibleMenuItems"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item flex items-center gap-3 px-4 py-3 rounded-xl transition-all"
          :class="{ 'mobile-nav-item-active': isActive(item.path) }"
          @click="toggleMobileMenu"
        >
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="isActive(item.path) ? 'bg-gradient-to-br from-primary to-secondary text-white' : 'bg-neutral-bg text-neutral-text-secondary'"
          >
            <i :class="item.icon" />
          </div>
          <div class="flex-1">
            <span
              class="text-lg font-semibold"
              :class="isActive(item.path) ? 'text-primary' : 'text-neutral-text'"
            >
              {{ item.label }}
            </span>
            <p class="text-sm text-neutral-text-disabled">
              {{ item.description }}
            </p>
          </div>
          <i
            v-if="isActive(item.path)"
            class="pi pi-check-circle text-primary text-xl"
          />
        </router-link>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
/**
 * TopNavbar - 顶部导航栏组件
 * 功能：提供完整的导航功能，包括水平菜单、搜索、主题切换、通知、用户信息等
 * 设计：游戏化风格，响应式布局，菜单水平显示
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { authStore, usePermission } from '@/composables/system/usePermission'
import ThemeSwitcher from '@/components/common/ThemeSwitcher.vue'

const router = useRouter()
const toast = useToast()
const { can } = usePermission()

const searchQuery = ref('')
const showNotifications = ref(false)
const showUserMenu = ref(false)
const mobileMenuOpen = ref(false)
const showLogoutConfirmDialog = ref(false)
const isLoggingOut = ref(false)

interface MenuItem {
  path: string
  label: string
  icon: string
  description?: string
  requireAuth?: boolean
}

const menuItems: MenuItem[] = [
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
    path: '/builds',
    label: '配置图书馆',
    icon: 'pi pi-book',
    description: '战场配置百科'
  },
  {
    path: '/build-parser',
    label: 'Build解析',
    icon: 'pi pi-code',
    description: '配置分析'
  },
  {
    path: '/settings',
    label: '系统设置',
    icon: 'pi pi-cog',
    description: '系统配置',
    requireAuth: true
  }
]

// 根据权限过滤菜单
const visibleMenuItems = computed(() => {
  return menuItems.filter(item => {
    if (item.requireAuth) {
      return can('write')
    }
    return true
  })
})

interface Notification {
  id: number
  type: 'log' | 'system' | 'achievement' | 'warning'
  title: string
  message: string
  time: string
  read: boolean
}

const notifications = ref<Notification[]>([
  {
    id: 1,
    type: 'log',
    title: '日志解析完成',
    message: '您上传的 zevtc 文件已成功解析，发现3个WVW战斗记录',
    time: '5分钟前',
    read: false
  },
  {
    id: 2,
    type: 'achievement',
    title: '成就解锁',
    message: '恭喜您！本周出勤次数达到10次，解锁"常胜将军"成就',
    time: '1小时前',
    read: false
  },
  {
    id: 3,
    type: 'system',
    title: '系统更新',
    message: 'GW2 WVW日志解析系统已更新至 v2.1.0，带来全新的UI体验',
    time: '昨天',
    read: true
  }
])

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isOperator = computed(() => authStore.currentRole === 'operator')
const user = computed(() => authStore.currentUser)
const userInitial = computed(() => {
  return user.value?.username?.charAt(0).toUpperCase() || 'A'
})

const currentPath = computed(() => router.currentRoute.value.path)

const isActive = (path: string) => {
  if (path === '/') {
    return currentPath.value === '/' || currentPath.value === '/dashboard'
  }
  return currentPath.value.startsWith(path)
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showNotifications.value = false
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const closeNotifications = () => {
  showNotifications.value = false
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    toast.add({
      severity: 'info',
      summary: '搜索功能',
      detail: `正在搜索: ${searchQuery.value}`,
      life: 3000
    })
  }
}

const handleLogout = async () => {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    toast.add({
      severity: 'success',
      summary: '登出成功',
      detail: '您已成功退出登录',
      life: 3000
    })
    router.push('/')
  } catch (error) {
    console.error('登出失败:', error)
    toast.add({
      severity: 'error',
      summary: '登出失败',
      detail: '请稍后重试',
      life: 3000
    })
  } finally {
    isLoggingOut.value = false
    showLogoutConfirmDialog.value = false
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
  toast.add({
    severity: 'success',
    summary: '操作成功',
    detail: '已全部标记为已读',
    life: 2000
  })
}

const handleNotificationClick = (notification: Notification) => {
  notification.read = true
  if (notification.type === 'log') {
    router.push('/logs')
  } else if (notification.type === 'system') {
    router.push('/settings')
  }
  closeNotifications()
}

const getNotificationIcon = (type: string) => {
  const icons: Record<string, string> = {
    log: 'pi pi-file text-base',
    system: 'pi pi-cog text-base',
    achievement: 'pi pi-trophy text-base',
    warning: 'pi pi-exclamation-triangle text-base'
  }
  return icons[type] || 'pi pi-bell text-base'
}

const getNotificationIconClass = (type: string) => {
  const classes: Record<string, string> = {
    log: 'bg-primary/10 text-primary',
    system: 'bg-secondary/10 text-secondary',
    achievement: 'bg-rarity-legendary/10 text-rarity-legendary',
    warning: 'bg-status-warning/10 text-status-warning'
  }
  return classes[type] || 'bg-neutral-bg text-neutral-text-secondary'
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.notification-dropdown') && !target.closest('.notification-btn')) {
    closeNotifications()
  }
  if (!target.closest('.user-dropdown') && !target.closest('.user-menu-trigger')) {
    closeUserMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ============================================
   导航栏字体优化方案
   - 默认：16px（标准型）
   - 大屏幕（≥1440px）：17px（宽松型）
   - 小屏幕（≤768px）：14px（紧凑型）
   ============================================ */

/* 导航项基础样式 */
.nav-item {
  color: var(--neutral-text-secondary);
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.6;
  letter-spacing: 0.02em;
}

.nav-item:hover {
  color: var(--neutral-text);
  background: var(--neutral-bg);
}

.nav-item-active {
  color: var(--primary) !important;
  background: var(--color-primary-alpha-10);
}

.nav-item .pi {
  font-size: 1rem;
}

/* Logo标题字体 */
header h1 {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5;
  letter-spacing: 0.01em;
}

/* Logo副标题字体 */
header p {
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.4;
  letter-spacing: 0.02em;
}

/* 大屏幕字体优化（≥1440px）- 宽松型 */
@media (min-width: 1440px) {
  .nav-item {
    font-size: 1.0625rem;
    line-height: 1.7;
    letter-spacing: 0.03em;
  }

  .nav-item .pi {
    font-size: 1.0625rem;
  }

  header h1 {
    font-size: 1.0625rem;
    line-height: 1.6;
  }

  header p {
    font-size: 0.9375rem;
    line-height: 1.5;
  }
}

/* 小屏幕字体优化（≤768px）- 紧凑型 */
@media (max-width: 768px) {
  .nav-item {
    font-size: 0.875rem;
    line-height: 1.5;
    letter-spacing: 0.01em;
  }

  .nav-item .pi {
    font-size: 0.875rem;
  }

  header h1 {
    font-size: 0.9375rem;
    line-height: 1.4;
  }

  header p {
    font-size: 0.8125rem;
    line-height: 1.3;
  }
}

/* 移动端菜单样式 */
.mobile-nav-item {
  background: var(--neutral-bg);
}

.mobile-nav-item:hover {
  background: var(--color-card-hover);
}

.mobile-nav-item-active {
  background: var(--color-primary-alpha-10) !important;
}

/* 下拉动画 */
.notification-dropdown,
.user-dropdown {
  animation: dropdown-appear 0.2s ease-out;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* 移动端全屏菜单动画 */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.3s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
}

.mobile-menu-enter-active > div,
.mobile-menu-leave-active > div {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.mobile-menu-enter-from > div,
.mobile-menu-leave-to > div {
  transform: translateY(-20px);
  opacity: 0;
}

/* 对话框缩放动画 */
.animate-scale-in {
  animation: scaleIn 0.25s ease-out forwards;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 淡出过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 无障碍：减少动画 */
@media (prefers-reduced-motion: reduce) {
  .notification-dropdown,
  .user-dropdown {
    animation: none;
  }

  .dropdown-enter-active,
  .dropdown-leave-active,
  .mobile-menu-enter-active,
  .mobile-menu-leave-active {
    transition: none;
  }

  .animate-scale-in {
    animation: none;
  }
}
</style>