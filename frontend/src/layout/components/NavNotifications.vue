<template>
  <div class="relative">
    <button
      class="relative p-2.5 hover:bg-neutral-bg rounded-xl transition-all hover:scale-105 group notification-btn"
      @click="show = !show"
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
        v-if="show"
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
            @click="$emit('mark-all-read')"
          >
            全部已读
          </button>
        </div>
        <div class="max-h-80 overflow-y-auto">
          <div
            v-for="notification in notifications"
            :key="notification.notice_id"
            class="px-4 py-3 hover:bg-neutral-bg/50 border-b border-neutral-border/50 last:border-b-0 transition-colors cursor-pointer"
            :class="{ 'bg-primary/5': !notification.is_read }"
            @click.stop="$emit('click', notification)"
          >
            <div class="flex items-start gap-3">
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                :class="getIconClass(notification.source_type)"
              >
                <i :class="getIcon(notification.source_type)" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-base font-medium text-neutral-text mb-0.5">
                  {{ notification.notice_title }}
                </p>
                <p class="text-sm text-neutral-text-secondary line-clamp-2">
                  {{ notification.notice_content }}
                </p>
                <p class="text-xs text-neutral-text-disabled mt-1">
                  {{ formatTime(notification.create_time) }}
                </p>
              </div>
              <div
                v-if="!notification.is_read"
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
</template>

<script setup lang="ts">
/**
 * 导航通知组件
 * 功能：通知按钮和下拉菜单
 */

import { ref } from 'vue'
import type { NoticeItem } from '@/services/system/noticeService'

const props = defineProps<{
  notifications: NoticeItem[]
  unreadCount: number
}>()

const emit = defineEmits<{
  'mark-all-read': []
  click: [notification: NoticeItem]
}>()

const show = ref(false)

const getIconClass = (sourceType: string | null) => {
  const map: Record<string, string> = {
    system: 'bg-primary/10 text-primary',
    parse: 'bg-secondary/10 text-secondary',
    score: 'bg-success/10 text-success',
    alert: 'bg-status-error/10 text-status-error',
  }
  return (sourceType && map[sourceType]) || 'bg-neutral-bg text-neutral-text-secondary'
}

const getIcon = (sourceType: string | null) => {
  const map: Record<string, string> = {
    system: 'pi pi-cog',
    parse: 'pi pi-file',
    score: 'pi pi-star',
    alert: 'pi pi-exclamation-triangle',
  }
  return (sourceType && map[sourceType]) || 'pi pi-bell'
}

const formatTime = (time: string | null) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}
</script>
