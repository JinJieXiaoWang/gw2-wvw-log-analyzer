<template>
  <div class="card relative overflow-hidden">
    <!-- 装饰性背景 -->
    <div
      class="absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30"
      style="background: radial-gradient(circle, var(--color-warning-alpha-10) 0%, transparent 70%)"
    />

    <div class="relative z-10">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-warning/20 to-secondary/10 flex items-center justify-center border border-warning/20">
          <i class="pi pi-bell text-status-warning text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            通知设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            管理系统通知方式和提醒偏好
          </p>
        </div>
      </div>

      <div class="space-y-4">
        <SettingItem
          title="邮件通知"
          description="接收重要事件的邮件通知，包括系统更新和安全警报"
          icon="pi pi-envelope"
          icon-color="primary"
        >
          <InputSwitch v-model="notificationSettings.email" />
        </SettingItem>
        <SettingItem
          title="推送通知"
          description="接收浏览器桌面推送通知，需要授权通知权限"
          icon="pi pi-bell"
          icon-color="secondary"
        >
          <InputSwitch v-model="notificationSettings.push" />
        </SettingItem>
        <SettingItem
          title="解析完成通知"
          description="日志解析完成后发送通知，方便及时查看结果"
          icon="pi pi-check-circle"
          icon-color="success"
        >
          <InputSwitch v-model="notificationSettings.parseComplete" />
        </SettingItem>
      </div>

      <!-- 保存按钮 -->
      <div class="flex justify-end mt-8 pt-6 border-t border-neutral-border">
        <BaseButton
          label="保存设置"
          icon="pi pi-check"
          @click="saveNotificationSettings"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 通知设置组件
 * 功能：显示和编辑通知设置
 * 更新日期：2026-05-04
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import InputSwitch from 'primevue/inputswitch'
import SettingItem from '../SettingItem.vue'

defineProps<{
  notificationSettings: {
    email: boolean
    push: boolean
    parseComplete: boolean
  }
}>()

const emit = defineEmits<{
  'save-notification-settings': []
}>()

const saveNotificationSettings = () => {
  emit('save-notification-settings')
}
</script>
