<template>
  <div class="card">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-neutral-text mb-1">
        系统信息
      </h3>
      <p class="text-sm text-neutral-text-secondary">
        查看系统运行状态
      </p>
    </div>

    <div class="space-y-4">
      <div class="p-4 bg-neutral-bg rounded-lg">
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="item in systemInfoItems"
            :key="item.label"
          >
            <p class="text-xs text-neutral-text-secondary mb-1">
              {{ item.label }}
            </p>
            <p class="text-sm text-neutral-text font-medium">
              {{ item.value }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { authStore } from '@/composables/system/usePermission'

const lastLoginTime = computed(() => {
  const user = authStore.currentUser
  if (user?.loginTime) {
    return new Date(user.loginTime).toLocaleString('zh-CN')
  }
  return '未知'
})

const systemInfoItems = computed(() => [
  { label: '系统版本', value: 'v1.0.0' },
  { label: '构建日期', value: '2024-01-15' },
  { label: '运行环境', value: 'Vue 3.4 + Vite 5.2' },
  { label: '最后登录', value: lastLoginTime.value },
])
</script>
