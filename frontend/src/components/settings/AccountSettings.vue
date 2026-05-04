<template>
  <div class="card">
    <!-- 装饰性背景 -->
    <div class="absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30"
      style="background: radial-gradient(circle, var(--color-primary-alpha-10) 0%, transparent 70%)"
    />

    <div class="relative">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/10 flex items-center justify-center border border-primary/20">
          <i class="pi pi-user text-primary text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            账号设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            管理您的账户信息和头像
          </p>
        </div>
      </div>

      <!-- 头像区域 -->
      <div class="flex items-start gap-6 mb-8">
        <div class="relative group">
          <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/20 transition-transform duration-300 group-hover:scale-105">
            <span class="text-white text-3xl font-bold">A</span>
          </div>
          <div class="absolute inset-0 rounded-2xl bg-neutral-card/80 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center cursor-pointer backdrop-blur-sm">
            <i class="pi pi-camera text-neutral-text text-xl" />
          </div>
        </div>
        <div class="flex-1">
          <h4 class="text-neutral-text font-semibold mb-2">
            头像
          </h4>
          <p class="text-sm text-neutral-text-secondary mb-3">
            支持 JPG、PNG 格式，文件大小不超过 2MB
          </p>
          <div class="flex gap-3">
            <Button
              label="更换头像"
              icon="pi pi-upload"
              size="small"
            />
            <Button
              label="移除"
              icon="pi pi-trash"
              size="small"
              severity="secondary"
              text
            />
          </div>
        </div>
      </div>

      <!-- 表单区域 -->
      <div class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-neutral-text">
              <i class="pi pi-user text-neutral-text-disabled mr-1.5 text-xs" />
              用户名
            </label>
            <InputText
              v-model="accountSettings.username"
              class="w-full"
              placeholder="请输入用户名"
            />
          </div>
          <div class="space-y-2">
            <label class="block text-sm font-medium text-neutral-text">
              <i class="pi pi-envelope text-neutral-text-disabled mr-1.5 text-xs" />
              邮箱
            </label>
            <InputText
              v-model="accountSettings.email"
              class="w-full"
              placeholder="请输入邮箱地址"
            />
          </div>
        </div>
        <div class="space-y-2">
          <label class="block text-sm font-medium text-neutral-text">
            <i class="pi pi-pencil text-neutral-text-disabled mr-1.5 text-xs" />
            个人简介
          </label>
          <Textarea
            v-model="accountSettings.bio"
            rows="3"
            class="w-full"
            placeholder="介绍一下你自己..."
          />
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="flex justify-end mt-8 pt-6 border-t border-neutral-border">
        <Button
          label="保存更改"
          icon="pi pi-check"
          severity="primary"
          @click="saveAccountSettings"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 账号设置组件
 * 功能：显示和编辑账号信息
 * 更新日期：2026-05-04
 */

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

defineProps<{
  accountSettings: {
    username: string
    email: string
    bio: string
  }
}>()

const emit = defineEmits<{
  'save-account-settings': []
}>()

const saveAccountSettings = () => {
  emit('save-account-settings')
}
</script>
