<template>
  <div class="card relative overflow-hidden">
    <!-- 装饰性背景 -->
    <div
      class="absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30"
      style="background: radial-gradient(circle, var(--color-error-alpha-10) 0%, transparent 70%)"
    />

    <div class="relative z-10">
      <!-- 卡片头部 -->
      <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-error/20 to-primary/10 flex items-center justify-center border border-error/20">
          <i class="pi pi-shield text-status-error text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-neutral-text">
            安全设置
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-0.5">
            管理账户安全、密码和会话状态
          </p>
        </div>
      </div>

      <div class="space-y-6">
        <!-- 账户安全 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-error/10 flex items-center justify-center">
              <i class="pi pi-lock text-status-error text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              账户安全
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="更改密码"
              description="定期更新密码以保障账户安全，建议使用强密码"
              icon="pi pi-key"
              icon-color="primary"
            >
              <Button
                label="更改密码"
                icon="pi pi-pencil"
                size="small"
                severity="secondary"
                outlined
                @click="showChangePasswordDialog = true"
              />
            </SettingItem>
            <SettingItem
              title="双因素认证"
              description="启用双因素认证，提高账户安全性"
              icon="pi pi-shield"
              icon-color="error"
            >
              <InputSwitch v-model="securitySettings.twoFactorAuth" />
            </SettingItem>
          </div>
        </div>

        <!-- 会话管理 -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-info/10 flex items-center justify-center">
              <i class="pi pi-desktop text-status-info text-sm" />
            </div>
            <h4 class="text-neutral-text font-semibold">
              会话管理
            </h4>
            <div class="flex-1 h-px bg-neutral-border ml-2" />
          </div>
          <div class="space-y-3">
            <SettingItem
              title="当前会话"
              :description="`上次登录: ${lastLoginTime}`"
              icon="pi pi-clock"
              icon-color="info"
            >
              <Button
                label="查看所有会话"
                icon="pi pi-list"
                size="small"
                severity="secondary"
                outlined
              />
            </SettingItem>
            <div class="p-4 bg-error/5 rounded-xl border border-error/10">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-error/10 flex items-center justify-center">
                    <i class="pi pi-sign-out text-status-error" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-neutral-text">
                      登出当前账户
                    </p>
                    <p class="text-xs text-neutral-text-secondary mt-0.5">
                      退出当前登录状态，需要重新登录
                    </p>
                  </div>
                </div>
                <Button
                  label="登出"
                  icon="pi pi-sign-out"
                  size="small"
                  severity="danger"
                  :loading="isLoggingOut"
                  @click="handleLogout"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 更改密码弹窗 -->
  <Dialog
    v-model:visible="showChangePasswordDialog"
    header="更改密码"
    modal
    :closable="!isChangingPassword"
    :close-on-escape="!isChangingPassword"
    class="w-full max-w-md"
    :destroy-on-hide="true"
  >
    <div class="space-y-4 pt-2">
      <!-- 旧密码 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-1.5">
          当前密码
        </label>
        <Password
          v-model="passwordForm.oldPassword"
          :feedback="false"
          toggle-mask
          placeholder="请输入当前密码"
          class="w-full"
          :input-class="'w-full'"
          @keydown.enter="handleChangePassword"
        />
      </div>

      <!-- 新密码 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-1.5">
          新密码
        </label>
        <Password
          v-model="passwordForm.newPassword"
          toggle-mask
          placeholder="请输入新密码"
          class="w-full"
          :input-class="'w-full'"
          prompt-label="请输入密码"
          weak-label="弱"
          medium-label="中"
          strong-label="强"
        />
        <p class="text-xs text-neutral-text-secondary mt-1">
          密码长度至少8位，需包含大小写字母和数字
        </p>
      </div>

      <!-- 确认新密码 -->
      <div>
        <label class="block text-sm font-medium text-neutral-text mb-1.5">
          确认新密码
        </label>
        <Password
          v-model="passwordForm.confirmPassword"
          :feedback="false"
          toggle-mask
          placeholder="请再次输入新密码"
          class="w-full"
          :input-class="'w-full'"
          :class="{ 'p-invalid': confirmPasswordError }"
          @keydown.enter="handleChangePassword"
        />
        <small
          v-if="confirmPasswordError"
          class="text-status-error block mt-1"
        >
          {{ confirmPasswordError }}
        </small>
      </div>

      <!-- 密码强度提示 -->
      <div
        v-if="passwordValidation.errors.length > 0"
        class="p-3 bg-warning/5 rounded-lg border border-warning/10"
      >
        <p class="text-xs font-medium text-status-warning mb-1">
          密码要求：
        </p>
        <ul class="space-y-0.5">
          <li
            v-for="error in passwordValidation.errors"
            :key="error"
            class="text-xs text-neutral-text-secondary flex items-center gap-1"
          >
            <i class="pi pi-times-circle text-status-error text-[10px]" />
            {{ error }}
          </li>
        </ul>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          label="取消"
          severity="secondary"
          outlined
          :disabled="isChangingPassword"
          @click="showChangePasswordDialog = false"
        />
        <Button
          label="确认更改"
          severity="primary"
          icon="pi pi-check"
          :loading="isChangingPassword"
          :disabled="!canSubmit"
          @click="handleChangePassword"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 安全设置组件
 * 功能：显示和编辑安全设置，对接更改密码、登出接口
 * 更新日期：2026-05-06
 */

import { ref, reactive, computed, onUnmounted } from 'vue'
import Button from 'primevue/button'
import InputSwitch from 'primevue/inputswitch'
import Dialog from 'primevue/dialog'
import Password from 'primevue/password'
import { useToast } from 'primevue/usetoast'
import SettingItem from './SettingItem.vue'
import { authService } from '@/services/auth/authService'
import { authStore } from '@/composables/system/usePermission'

defineProps<{
  securitySettings: {
    twoFactorAuth: boolean
  }
  lastLoginTime: string
}>()

const emit = defineEmits<{
  'logout': []
  'update:securitySettings': [settings: { twoFactorAuth: boolean }]
}>()

const toast = useToast()

// ============================================
// 登出
// ============================================
const isLoggingOut = ref(false)

const handleLogout = async () => {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    emit('logout')
  } catch (error) {
    console.error('Logout failed:', error)
    toast.add({
      severity: 'error',
      summary: '登出失败',
      detail: '请稍后重试',
      life: 3000
    })
  } finally {
    isLoggingOut.value = false
  }
}

// ============================================
// 更改密码
// ============================================
const showChangePasswordDialog = ref(false)
const isChangingPassword = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const confirmPasswordError = computed(() => {
  if (!passwordForm.confirmPassword) return ''
  if (passwordForm.confirmPassword !== passwordForm.newPassword) {
    return '两次输入的密码不一致'
  }
  return ''
})

const passwordValidation = computed(() => {
  return authStore.validatePassword(passwordForm.newPassword)
})

const canSubmit = computed(() => {
  return (
    passwordForm.oldPassword.length > 0 &&
    passwordForm.newPassword.length > 0 &&
    passwordForm.confirmPassword.length > 0 &&
    passwordForm.newPassword === passwordForm.confirmPassword &&
    passwordValidation.value.valid
  )
})

const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const handleChangePassword = async () => {
  if (!canSubmit.value) return

  isChangingPassword.value = true
  const payload = {
    current_password: passwordForm.oldPassword,
    new_password: passwordForm.newPassword,
    confirm_password: passwordForm.confirmPassword
  }
  console.log('[ChangePassword] Sending payload:', payload)

  try {
    const result = await authService.changePassword(payload)
    console.log('[ChangePassword] Response:', result)

    // 兼容两种后端响应格式：{ success: true } 或 { code: 200 }
    const isSuccess = result?.success === true || (result?.code >= 200 && result?.code < 300)

    if (isSuccess) {
      toast.add({
        severity: 'success',
        summary: '密码已更改',
        detail: '请使用新密码重新登录',
        life: 3000
      })
      showChangePasswordDialog.value = false
      resetPasswordForm()

      // 延迟后自动登出，要求用新密码重新登录
      setTimeout(() => {
        authStore.logout().then(() => {
          emit('logout')
        })
      }, 1500)
    } else {
      toast.add({
        severity: 'error',
        summary: '更改失败',
        detail: result?.message || result?.msg || '请检查当前密码是否正确',
        life: 3000
      })
    }
  } catch (error: any) {
    console.error('[ChangePassword] Error:', error)
    const detail =
      error?.response?.data?.message ||
      error?.response?.data?.msg ||
      error?.message ||
      '网络异常，请稍后重试'
    toast.add({
      severity: 'error',
      summary: '更改失败',
      detail,
      life: 3000
    })
  } finally {
    isChangingPassword.value = false
  }
}

// 组件卸载时清理状态，防止影响其他页面
onUnmounted(() => {
  showChangePasswordDialog.value = false
  isChangingPassword.value = false
  isLoggingOut.value = false
  resetPasswordForm()
})
</script>
