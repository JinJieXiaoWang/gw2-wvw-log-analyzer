<template>
  <div class="card">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-neutral-text mb-1">
        安全设置
      </h3>
      <p class="text-sm text-neutral-text-secondary">
        配置登录安全策略
      </p>
    </div>

    <div class="space-y-6 max-w-2xl">
      <div class="flex items-center justify-between p-4 bg-neutral-bg rounded-lg">
        <div>
          <h4 class="text-sm font-medium text-neutral-text mb-1">
            登录失败锁定
          </h4>
          <p class="text-xs text-neutral-text-secondary">
            连续5次登录失败后锁定账号15分钟
          </p>
        </div>
        <span class="px-3 py-1 bg-status-success/10 text-status-success text-sm rounded-full">已启用</span>
      </div>

      <div class="flex items-center justify-between p-4 bg-neutral-bg rounded-lg">
        <div>
          <h4 class="text-sm font-medium text-neutral-text mb-1">
            密码加密存储
          </h4>
          <p class="text-xs text-neutral-text-secondary">
            使用强哈希算法加密存储密码
          </p>
        </div>
        <span class="px-3 py-1 bg-status-success/10 text-status-success text-sm rounded-full">已启用</span>
      </div>

      <div class="flex items-center justify-between p-4 bg-neutral-bg rounded-lg">
        <div>
          <h4 class="text-sm font-medium text-neutral-text mb-1">
            会话超时
          </h4>
          <p class="text-xs text-neutral-text-secondary">
            设置登录状态保持时间
          </p>
        </div>
        <Dropdown
          v-model="sessionTimeout"
          :options="sessionTimeoutOptions"
          option-label="label"
          option-value="value"
          class="w-40"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Dropdown from 'primevue/dropdown'

import { SESSION_TIMEOUT_OPTIONS } from '@/constants/options'
const sessionTimeoutOptions = SESSION_TIMEOUT_OPTIONS

const sessionTimeout = ref(60)
</script>
