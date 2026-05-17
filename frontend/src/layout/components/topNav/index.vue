<template>
  <header
    class="h-16 backdrop-blur-xl bg-neutral-card/60 border-b border-neutral-border/50 flex items-center justify-between px-4 lg:px-6 flex-shrink-0 sticky top-0 z-50 transition-all duration-300"
  >
    <!-- 底部主题色渐变线 -->
    <div class="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary/40 to-transparent pointer-events-none" />
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
      <BaseMenubar
        v-model:mobile-open="mobileMenuOpen"
        :model="menuData"
        :active-route="currentPath"
        @navigate="handleNavigate"
      />
    </div>

    <!-- 右侧功能区 -->
    <div class="flex items-center gap-2 sm:gap-3">
      <!-- 搜索框 -->
      <div class="hidden xl:flex items-center relative group">
        <BaseInput
          v-model="searchQuery"
          placeholder="搜索日志、玩家..."
          class="w-72 pl-11"
          @keyup.enter="handleSearch"
        />
        <i class="pi pi-search absolute left-4 top-1/2 -translate-y-1/2 text-neutral-text-disabled group-hover:text-primary transition-colors pointer-events-none" />
        <kbd class="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-1 bg-neutral-bg border border-neutral-border rounded text-xs text-neutral-text-disabled hidden group-hover:flex items-center gap-1"><span>⌘</span><span>K</span></kbd>
      </div>

      <ThemeSwitcher />

      <BaseButton
        class="xl:hidden p-2.5"
        severity="secondary"
        variant="text"
        icon="pi pi-search"
        @click="handleSearch"
      />

      <NavNotifications
        v-if="isOperator"
        :notifications="notifications"
        :unread-count="unreadCount"
        @mark-all-read="markAllAsRead"
        @click="handleNotificationClick"
      />

      <!-- 用户菜单 -->
      <div class="relative">
        <BaseButton
          class="user-menu-trigger flex items-center gap-2 p-1.5 pr-3 hover:scale-[1.02]"
          severity="secondary"
          variant="text"
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
        </BaseButton>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '@/composables/system/usePermission'
import { noticeService } from '@/services/system/noticeService'
import type { NoticeItem } from '@/services/system/noticeService'
import ThemeSwitcher from '@/components/common/theme/ThemeSwitcher.vue'
import LogoutConfirmDialog from '@/layout/components/LogoutConfirmDialog.vue'
import NavNotifications from '@/layout/components/NavNotifications.vue'
import UserDropdownMenu from './UserDropdownMenu.vue'
import BaseMenubar from '@/components/common/ui/navigation/BaseMenubar.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import { useTopNav } from '@/composables/layout/useTopNav'

const router = useRouter()
const {
  searchQuery, showUserMenu, showLogoutConfirmDialog, isLoggingOut,
  isAuthenticated, isOperator, user, userInitial, canWrite,
  currentPath, menuData, handleSearch, handleLogout, handleNavigate, handleClickOutside,
} = useTopNav()

// === 通知状态（保留在组件层，避免 composable 过大） ===
const notifications = ref<NoticeItem[]>([])
const unreadCount = ref(0)
const mobileMenuOpen = ref(false)

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
