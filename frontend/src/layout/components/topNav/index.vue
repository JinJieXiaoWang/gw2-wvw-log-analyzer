<template>
  <header
    class="h-16 backdrop-blur-md border-b flex items-center justify-between px-4 lg:px-6 flex-shrink-0 sticky top-0 z-50 transition-all duration-300"
    :style="{ backgroundColor: 'var(--color-card)', borderColor: 'var(--color-border)', boxShadow: '0 1px 3px var(--color-shadow)' }"
  >
    <div class="flex items-center gap-6">
      <!-- Logo -->
      <router-link
        to="/"
        class="flex items-center gap-3 group"
      >
        <div class="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg shadow-primary/30 relative overflow-hidden group-hover:scale-105 transition-transform bg-neutral-card">
          <img
            src="@/assets/fonts/logo.png"
            alt="GW2 Logo"
            class="w-10 h-10 object-contain"
          >
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

      <!-- 主导航 -->
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
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-300 group-hover:w-3/4" />
          <div
            v-if="isActive(item.path)"
            class="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-0.5 bg-gradient-to-r from-primary to-secondary rounded-full"
          />
        </router-link>
      </nav>
    </div>

    <!-- 右侧功能区 -->
    <div class="flex items-center gap-2 sm:gap-3">
      <!-- 搜索框 -->
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
          <kbd class="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-1 bg-neutral-bg border border-neutral-border rounded text-xs text-neutral-text-disabled hidden group-hover:flex items-center gap-1"><span>⌘</span><span>K</span></kbd>
        </div>
      </div>

      <ThemeSwitcher />

      <button class="xl:hidden p-2.5 hover:bg-neutral-bg rounded-xl transition-colors">
        <i class="pi pi-search text-neutral-text-secondary text-lg" />
      </button>
      <button
        class="lg:hidden p-2.5 hover:bg-neutral-bg rounded-xl transition-colors"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <i
          :class="mobileMenuOpen ? 'pi pi-times' : 'pi pi-bars'"
          class="text-neutral-text-secondary text-lg"
        />
      </button>

      <NavNotifications
        v-if="isOperator"
        :notifications="notifications"
        :unread-count="unreadCount"
        @mark-all-read="markAllAsRead"
        @click="handleNotificationClick"
      />

      <!-- 用户菜单 -->
      <div class="relative">
        <button
          class="flex items-center gap-2 p-1.5 pr-3 hover:bg-neutral-bg rounded-xl transition-all hover:scale-[1.02] user-menu-trigger"
          @click="showUserMenu = !showUserMenu"
        >
          <div class="relative">
            <div class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-md shadow-primary/20 overflow-hidden ring-2 ring-primary/20">
              <span class="text-white font-bold text-base">{{ userInitial }}</span>
            </div>
            <div class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-status-success rounded-full border-2 border-neutral-card" />
          </div>
          <div class="hidden sm:block text-left">
            <p class="text-base font-semibold text-neutral-text leading-tight">
              {{ isAuthenticated ? (user?.username || '操作员') : '游客' }}
            </p>
            <span
              :class="isAuthenticated ? 'text-primary' : 'text-neutral-text-disabled'"
              class="text-sm"
            >{{ isAuthenticated ? '操作员' : '浏览模式' }}</span>
          </div>
          <i class="pi pi-chevron-down text-sm text-neutral-text-disabled hidden sm:block" />
        </button>
        <UserDropdownMenu
          :visible="showUserMenu"
          :is-authenticated="isAuthenticated"
          :user="user"
          :user-initial="userInitial"
          :can-write="canWrite"
          @close="showUserMenu = false"
          @logout="showLogoutConfirmDialog = true"
        />
      </div>
    </div>
  </header>

  <LogoutConfirmDialog
    v-model:visible="showLogoutConfirmDialog"
    :is-logging-out="isLoggingOut"
    @confirm="handleLogout"
  />
  <MobileNavMenu
    v-model:visible="mobileMenuOpen"
    :items="visibleMenuItems"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { authStore, usePermission } from '@/composables/system/usePermission'
import { noticeService } from '@/services/system/noticeService'
import type { NoticeItem } from '@/services/system/noticeService'
import ThemeSwitcher from '@/components/common/theme/ThemeSwitcher.vue'
import LogoutConfirmDialog from '@/layout/components/LogoutConfirmDialog.vue'
import MobileNavMenu from '@/layout/components/MobileNavMenu.vue'
import NavNotifications from '@/layout/components/NavNotifications.vue'
import UserDropdownMenu from './UserDropdownMenu.vue'
import { menuItems as fallbackMenuItems } from './menuConfig'

const router = useRouter()
const toast = useToast()
const { can } = usePermission()

const searchQuery = ref('')
const showUserMenu = ref(false)
const mobileMenuOpen = ref(false)
const showLogoutConfirmDialog = ref(false)
const isLoggingOut = ref(false)

// 展平树形菜单结构，只保留可直接访问的菜单项
function flattenMenus(menus: any[]): any[] {
  let result: any[] = []
  menus.forEach(menu => {
    if (menu.menu_type === 'C' && menu.path) {
      result.push({
        path: menu.path || '',
        label: menu.menu_name || '',
        icon: menu.icon ? `pi pi-${menu.icon}` : 'pi pi-circle',
        description: menu.remark || '',
        requireAuth: !!menu.perms,
        perms: menu.perms
      })
    }
    if (menu.children && menu.children.length > 0) {
      result = result.concat(flattenMenus(menu.children))
    }
  })
  return result
}

// 使用后端API获取的菜单数据，如果没有则使用硬编码的备用菜单
const backendMenuItems = computed(() => {
  const menus = authStore.menus || []
  if (menus.length === 0) {
    return fallbackMenuItems
  }
  
  // 展平树形菜单
  return flattenMenus(menus)
})

const visibleMenuItems = computed(() => {
  return backendMenuItems.value.filter(item => {
    if (!item.requireAuth) {
      return true
    }
    if (!can('write')) {
      return false
    }
    // 检查具体权限，系统设置需要manage_users权限
    if (item.perms) {
      const requiredPerms = item.perms.split(',')
      return requiredPerms.some(p => can(p as any))
    }
    return true
  })
})

const notifications = ref<NoticeItem[]>([])
const unreadCount = ref(0)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isOperator = computed(() => authStore.currentRole === 'operator' || authStore.currentRole === 'super_admin')
const user = computed(() => authStore.currentUser)
const userInitial = computed(() => user.value?.username?.charAt(0).toUpperCase() || 'A')
const canWrite = computed(() => can('write'))

const currentPath = computed(() => router.currentRoute.value.path)
const isActive = (path: string) => path === '/' ? (currentPath.value === '/' || currentPath.value === '/dashboard') : currentPath.value.startsWith(path)

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    toast.add({ severity: 'info', summary: '搜索功能', detail: `正在搜索: ${searchQuery.value}`, life: 3000 })
  }
}

const handleLogout = async () => {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    toast.add({ severity: 'success', summary: '登出成功', detail: '您已成功退出登录', life: 3000 })
    router.push('/')
  } catch {
    toast.add({ severity: 'error', summary: '登出失败', detail: '请稍后重试', life: 3000 })
  } finally {
    isLoggingOut.value = false
    showLogoutConfirmDialog.value = false
  }
}

async function loadNotifications() {
  if (!isAuthenticated.value) return
  try {
    const result = await noticeService.getNoticeList({ page: 1, page_size: 20 })
    if (result.success && result.data) notifications.value = result.data.items || []
  } catch (e) { console.error('加载通知失败', e) }
}

async function loadUnreadCount() {
  if (!isAuthenticated.value) return
  try {
    const result = await noticeService.getUnreadCount()
    if (result.success && result.data) unreadCount.value = result.data.count || 0
  } catch (e) { console.error('加载未读数失败', e) }
}

async function markAllAsRead() {
  try {
    const result = await noticeService.markAllAsRead()
    if (result.success) {
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
      toast.add({ severity: 'success', summary: '操作成功', detail: '已全部标记为已读', life: 2000 })
    }
  } catch (e) { console.error('标记全部已读失败', e) }
}

async function handleNotificationClick(notification: NoticeItem) {
  if (!notification.is_read) {
    try {
      await noticeService.markAsRead(notification.notice_id)
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (e) { console.error('标记已读失败', e) }
  }
  if (notification.source_type === 'parse_failed') router.push('/logs')
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-dropdown') && !target.closest('.user-menu-trigger')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  if (isAuthenticated.value) {
    loadNotifications()
    loadUnreadCount()
    const interval = setInterval(loadUnreadCount, 30000)
    onUnmounted(() => clearInterval(interval))
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>@import './topNav.css';</style>
