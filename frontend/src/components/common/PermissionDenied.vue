<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <div class="w-20 h-20 bg-status-error/10 rounded-full flex items-center justify-center mb-6">
      <i class="pi pi-lock text-status-error text-4xl" />
    </div>
    <h3 class="text-xl font-semibold text-neutral-text mb-2">
      权限不足
    </h3>
    <p class="text-neutral-text-secondary text-center mb-6 max-w-md">
      {{ message || '您当前的身份无法执行此操作，请登录管理员账号或联系系统管理员' }}
    </p>
    <div class="flex gap-3">
      <Button
        v-if="showLoginButton"
        label="登录管理员账号"
        icon="pi pi-sign-in"
        @click="goToLogin"
      />
      <Button
        label="返回首页"
        severity="secondary"
        icon="pi pi-home"
        @click="goHome"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'

defineProps<{
  message?: string
  showLoginButton?: boolean
}>()

const router = useRouter()

const goToLogin = () => {
  router.push({
    path: '/login',
    query: { redirect: router.currentRoute.value.fullPath }
  })
}

const goHome = () => {
  router.push('/home')
}
</script>
