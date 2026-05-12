<template>
  <div class="card">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-semibold text-neutral-text mb-1">
          账号管理
        </h3>
        <p class="text-sm text-neutral-text-secondary">
          修改管理员登录凭据
        </p>
      </div>
    </div>

    <div class="space-y-4 max-w-2xl">
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">当前用户名</label>
        <InputText
          v-model="accountForm.username"
          placeholder="请输入用户名"
          class="w-full"
        />
        <small class="text-neutral-text-disabled text-xs">用户名长度至少3个字符</small>
      </div>

      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">新密码</label>
        <Password
          v-model="accountForm.newPassword"
          placeholder="请输入新密码（留空则不修改）"
          toggle-mask
          class="w-full"
          input-class="w-full"
        />
      </div>

      <div>
        <label class="block text-sm text-neutral-text-secondary mb-2">确认新密码</label>
        <Password
          v-model="accountForm.confirmPassword"
          placeholder="请再次输入新密码"
          toggle-mask
          class="w-full"
          input-class="w-full"
        />
      </div>

      <div class="p-4 bg-neutral-bg rounded-lg">
        <h4 class="text-sm font-medium text-neutral-text mb-3">
          密码要求
        </h4>
        <div class="space-y-2">
          <div
            v-for="req in passwordRequirements"
            :key="req.key"
            class="flex items-center gap-2 text-sm"
          >
            <i
              class="pi"
              :class="req.met ? 'pi-check text-status-success' : 'pi-times text-status-error'"
            />
            <span :class="req.met ? 'text-status-success' : 'text-status-error'">{{ req.label }}</span>
          </div>
        </div>
      </div>

      <div
        v-if="errors"
        class="p-3 bg-status-error/10 border border-status-error/30 rounded-lg"
      >
        <div class="flex items-center gap-2 text-status-error text-sm">
          <i class="pi pi-exclamation-circle" />
          <span>{{ errors }}</span>
        </div>
      </div>

      <div class="flex gap-3 pt-4">
        <BaseButton
          label="保存修改"
          icon="pi pi-save"
          :loading="saving"
          @click="save"
        />
        <BaseButton
          label="重置"
          variant="secondary"
          icon="pi pi-refresh"
          @click="reset"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { authStore } from '@/composables/system/usePermission'

const toast = useToast()
const saving = ref(false)
const errors = ref('')

const accountForm = reactive({
  username: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordValidation = computed(() => {
  const password = accountForm.newPassword || ''
  return {
    hasMinLength: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecialChar: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)
  }
})

const passwordRequirements = computed(() => [
  { key: 'length', label: '至少8个字符', met: passwordValidation.value.hasMinLength },
  { key: 'upper', label: '包含大写字母', met: passwordValidation.value.hasUppercase },
  { key: 'lower', label: '包含小写字母', met: passwordValidation.value.hasLowercase },
  { key: 'number', label: '包含数字', met: passwordValidation.value.hasNumber },
  { key: 'special', label: '包含特殊字符', met: passwordValidation.value.hasSpecialChar },
])

const save = async () => {
  errors.value = ''
  if (!accountForm.username || accountForm.username.length < 3) {
    errors.value = '用户名长度至少3个字符'
    return
  }
  if (accountForm.newPassword) {
    const validation = authStore.validatePassword(accountForm.newPassword)
    if (!validation.valid) {
      errors.value = validation.errors.join('；')
      return
    }
    if (accountForm.newPassword !== accountForm.confirmPassword) {
      errors.value = '两次输入的密码不一致'
      return
    }
  }
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    if (accountForm.newPassword) {
      const result = authStore.setAdminConfig(accountForm.username, accountForm.newPassword)
      if (!result.success) {
        errors.value = result.message
        return
      }
    } else {
      const currentConfig = authStore.getAdminConfig()
      localStorage.setItem('gw2_wvw_admin_config', JSON.stringify({
        username: accountForm.username,
        password: currentConfig.password
      }))
    }
    toast.add({ severity: 'success', summary: '保存成功', detail: '管理员账号配置已更新', life: 3000 })
    accountForm.newPassword = ''
    accountForm.confirmPassword = ''
  } catch {
    toast.add({ severity: 'error', summary: '保存失败', detail: '发生错误，请稍后重试', life: 3000 })
  } finally {
    saving.value = false
  }
}

const reset = () => {
  const config = authStore.getAdminConfig()
  accountForm.username = config.username
  accountForm.newPassword = ''
  accountForm.confirmPassword = ''
  errors.value = ''
}

defineExpose({ reset })
</script>
