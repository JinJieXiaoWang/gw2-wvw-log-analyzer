<template>
  <div class="flex items-center justify-center min-h-[60vh]">
    <PermissionDenied
      message="您没有权限访问该页面，请确认您已使用管理员账号登录"
      :show-login-button="!isAuthenticated"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PermissionDenied from '@/layout/components/PermissionDenied.vue'
import { authStore } from '@/composables/system/usePermission'

const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>
