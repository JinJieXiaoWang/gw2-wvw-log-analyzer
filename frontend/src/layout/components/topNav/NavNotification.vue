<template>
  <div v-if="isOperator" class="relative">
    <button class="relative p-2.5 hover:bg-neutral-bg rounded-xl transition-all hover:scale-105 group notification-btn" @click="toggleNotifications">
      <i class="pi pi-bell text-neutral-text-secondary group-hover:text-primary transition-colors text-xl" />
      <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 min-w-[20px] h-5 bg-gradient-to-r from-status-error to-secondary text-white text-xs font-bold rounded-full flex items-center justify-center px-1.5 shadow-lg animate-pulse">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>
    <transition name="dropdown" appear>
      <div v-if="showNotifications" class="notification-dropdown absolute top-full mt-2 right-0 w-80 sm:w-96 bg-neutral-card border border-neutral-border rounded-xl shadow-2xl shadow-neutral-shadow/50 overflow-hidden z-50">
        <div class="px-4 py-3 border-b border-neutral-border bg-gradient-to-r from-primary/5 to-secondary/5 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span class="text-base font-bold text-neutral-text">֪ͨ中心</span>
          </div>
          <button v-if="unreadCount > 0" class="text-sm text-primary hover:text-primary/80 transition-colors" @click.stop="markAllAsRead">ȫ部已读</button>
        </div>
        <div class="max-h-80 overflow-y-auto">
          <div v-for="notification in notifications" :key="notification.notice_id" class="px-4 py-3 hover:bg-neutral-bg/50 border-b border-neutral-border/50 last:border-b-0 transition-colors cursor-pointer" :class="{ 'bg-primary/5': !notification.is_read }" @click.stop="handleNotificationClick(notification)">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="getNotificationIconClass(notification.source_type)">
                <i :class="getNotificationIcon(notification.source_type)" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-base font-medium text-neutral-text mb-0.5">{{ notification.notice_title }}</p>
                <p class="text-sm text-neutral-text-secondary line-clamp-2">{{ notification.notice_content }}</p>
                <p class="text-xs text-neutral-text-disabled mt-1">{{ formatTime(notification.create_time) }}</p>
              </div>
              <div v-if="!notification.is_read" class="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-2" />
            </div>
          </div>
          <div v-if="notifications.length === 0" class="py-12 text-center">
            <i class="pi pi-bell-slash text-4xl text-neutral-text-disabled mb-2" />
            <p class="text-base text-neutral-text-secondary">暂无֪ͨ</p>
          </div>
        </div>
        <div class="px-4 py-2 border-t border-neutral-border bg-neutral-bg/50 text-center">
          <button class="text-base text-primary hover:text-primary/80 transition-colors">查看全部֪ͨ</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '@/composables/system/usePermission'
import { noticeService } from '@/services/system/noticeService'
import type { NoticeItem } from '@/services/system/noticeService'

const router = useRouter()
const showNotifications = ref(false)
const notifications = ref<NoticeItem[]>([])
const unreadCount = ref(0)
const isLoadingNotifications = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isOperator = computed(() => authStore.currentRole === 'operator' || authStore.currentRole === 'super_admin')

let unreadCountInterval: ReturnType<typeof setInterval> | null = null

const toggleNotifications = async () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value && notifications.value.length === 0) await loadNotifications()
}

const loadNotifications = async () => {
  if (!isAuthenticated.value) return
  try {
    isLoadingNotifications.value = true
    const result = await noticeService.getNoticeList({ page: 1, page_size: 20 })
    if (result.success && result.data) notifications.value = result.data.items || []
  } catch (e) { console.error('加载通知失败:', e) }
  finally { isLoadingNotifications.value = false }
}

const loadUnreadCount = async () => {
  if (!isAuthenticated.value) return
  try {
    const result = await noticeService.getUnreadCount()
    if (result.success && result.data) unreadCount.value = result.data.count || 0
  } catch (e) { console.error('加载未读通知数失败:', e) }
}

const markAllAsRead = async () => {
  try {
    const result = await noticeService.markAllAsRead()
    if (result.success) {
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    }
  } catch (e) { console.error('标记全部已读失败:', e) }
}

const handleNotificationClick = async (notification: NoticeItem) => {
  if (!notification.is_read) {
    try {
      await noticeService.markAsRead(notification.notice_id)
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (e) { console.error('标记已读失败:', e) }
  }
  if (notification.source_type === 'parse_failed') router.push('/logs')
  showNotifications.value = false
}

const getNotificationIcon = (sourceType: string | null) => {
  const icons: Record<string, string> = { parse_failed: 'pi pi-exclamation-triangle text-base', parse_complete: 'pi pi-check-circle text-base', system: 'pi pi-cog text-base' }
  return icons[sourceType || ''] || 'pi pi-bell text-base'
}

const getNotificationIconClass = (sourceType: string | null) => {
  const classes: Record<string, string> = { parse_failed: 'bg-status-error/10 text-status-error', parse_complete: 'bg-status-success/10 text-status-success', system: 'bg-secondary/10 text-secondary' }
  return classes[sourceType || ''] || 'bg-neutral-bg text-neutral-text-secondary'
}

const formatTime = (timeStr: string | null) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟ǰ`
  if (hours < 24) return `${hours}Сʱǰ`
  if (days < 7) return `${days}天ǰ`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  if (isAuthenticated.value) {
    loadUnreadCount()
    unreadCountInterval = setInterval(loadUnreadCount, 30000)
  }
})

onUnmounted(() => {
  if (unreadCountInterval) { clearInterval(unreadCountInterval); unreadCountInterval = null }
})
</script>
