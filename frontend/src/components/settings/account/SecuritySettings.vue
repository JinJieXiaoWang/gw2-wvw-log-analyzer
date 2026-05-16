<template>
  <div class="card relative overflow-hidden">
    <div class="deco-bg-error" />

    <div class="relative z-10">
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
              <BaseButton
                label="更改密码"
                icon="pi pi-pencil"
                size="small"
                variant="secondary"
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
              <BaseToggleSwitch
                :model-value="securitySettings.twoFactorAuth"
                @update:model-value="updateTwoFactor"
              />
            </SettingItem>
          </div>
        </div>

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
              :description="`上次登录: ${lastLoginTime || '未知'}`"
              icon="pi pi-clock"
              icon-color="info"
            >
              <BaseButton
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
                <BaseButton
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

    <ChangePasswordDialog
      v-model:visible="showChangePasswordDialog"
      @success="onPasswordChanged"
    />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseToggleSwitch from '@/components/common/ui/input/BaseToggleSwitch.vue'
import { authStore } from '@/composables/system/usePermission'
import { useToast } from 'primevue/usetoast'
import { ref } from 'vue'
import SettingItem from '../SettingItem.vue'
import ChangePasswordDialog from './ChangePasswordDialog.vue'

interface Props {
  securitySettings: {
    twoFactorAuth: boolean
  }
  lastLoginTime: string
}

withDefaults(defineProps<Props>(), {
  securitySettings: () => ({ twoFactorAuth: false }),
  lastLoginTime: ''
})

const emit = defineEmits<{
  logout: []
  'update:securitySettings': [settings: { twoFactorAuth: boolean }]
}>()

const toast = useToast()
// authStore 单例已从 usePermission 导入
const isLoggingOut = ref(false)
const showChangePasswordDialog = ref(false)

const handleLogout = async () => {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    emit('logout')
  } catch (error) {
    console.error('Logout failed:', error)
    toast.add({ severity: 'error', summary: '登出失败', detail: '请稍后重试', life: 3000 })
  } finally {
    isLoggingOut.value = false
  }
}

const onPasswordChanged = () => {
  setTimeout(() => {
    authStore.logout().then(() => {
      emit('logout')
    })
  }, 1500)
}

const updateTwoFactor = (value: boolean) => {
  emit('update:securitySettings', { twoFactorAuth: value })
}
</script>

<style scoped>
.deco-bg-error {
  @apply absolute top-0 right-0 w-64 h-64 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none opacity-30;
  background: radial-gradient(circle, var(--color-error-alpha-10) 0%, transparent 70%);
}
</style>
