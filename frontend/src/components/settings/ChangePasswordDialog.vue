<template>
  <BaseDialog v-model:visible="visible" header="更改密码" :modal="true" :closable="!isChangingPassword" :close-on-escape="!isChangingPassword" width="448" confirm-label="确认更改" confirm-icon="pi pi-check" :loading="isChangingPassword" :confirm-disabled="!canSubmit" :destroy-on-hide="true" @confirm="submit">
    <div class="space-y-4 pt-2">
      <FormField label="当前密码">
        <Password v-model="form.oldPassword" :feedback="false" toggle-mask placeholder="请输入当前密码" class="w-full" :input-class="'w-full'" @keydown.enter="submit" />
      </FormField>
      <FormField label="新密码" hint="密码长度至少8位，需包含大小写字母和数字">
        <Password v-model="form.newPassword" toggle-mask placeholder="请输入新密码" class="w-full" :input-class="'w-full'" prompt-label="请输入密码" weak-label="弱" medium-label="中" strong-label="强" />
      </FormField>
      <FormField label="确认新密码" :error="confirmError">
        <Password v-model="form.confirmPassword" :feedback="false" toggle-mask placeholder="请再次输入新密码" class="w-full" :input-class="'w-full'" :class="{ 'p-invalid': confirmError }" @keydown.enter="submit" />
      </FormField>
      <div v-if="validation.errors.length > 0" class="p-3 bg-warning/5 rounded-lg border border-warning/10">
        <p class="text-xs font-medium text-status-warning mb-1">密码要求：</p>
        <ul class="space-y-0.5">
          <li v-for="error in validation.errors" :key="error" class="text-xs text-neutral-text-secondary flex items-center gap-1">
            <i class="pi pi-times-circle text-status-error text-[10px]" /> {{ error }}
          </li>
        </ul>
      </div>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
import { reactive, computed, watch, ref } from 'vue'
import BaseDialog from '@/components/common/ui/BaseDialog.vue'
import Password from 'primevue/password'
import FormField from '@/components/common/ui/FormField.vue'
import { useToast } from 'primevue/usetoast'
import { authService } from '@/services/auth/authService'
import { authStore } from '@/composables/system/usePermission'
import { configManager } from '@/services/core/configManager'

const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{ (e: 'logout'): void }>()

const toast = useToast()
const isChangingPassword = ref(false)
const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const confirmError = computed(() => {
  if (!form.confirmPassword) return ''
      return form.confirmPassword !== form.newPassword ? '两次输入的密码不一致' : ''
})

const validation = computed(() => authStore.validatePassword(form.newPassword))
const canSubmit = computed(() => form.oldPassword && form.newPassword && form.confirmPassword && form.newPassword === form.confirmPassword && validation.value.valid)

const reset = () => { form.oldPassword = ''; form.newPassword = ''; form.confirmPassword = '' }
watch(visible, (v) => { if (v) reset() })

const submit = async () => {
  if (!canSubmit.value) return
  isChangingPassword.value = true
  try {
    const result = await authService.changePassword({ current_password: form.oldPassword, new_password: form.newPassword })
    const isSuccess = result?.success === true || (result?.code >= 200 && result?.code < 300)
    if (isSuccess) {
      toast.add({ severity: 'success', summary: '密码已更改', detail: '请使用新密码重新登录', life: configManager.get('ui').toastLife })
      visible.value = false
      reset()
      setTimeout(() => { authStore.logout().then(() => emit('logout')) }, 1500)
    } else {
      toast.add({ severity: 'error', summary: '更改失败', detail: result?.message || result?.msg || '请检查当前密码是否正确', life: configManager.get('ui').toastLife })
    }
  } catch (error: any) {
    const detail = error?.response?.data?.message || error?.response?.data?.msg || error?.message || '网络异常，请稍后重试'
    toast.add({ severity: 'error', summary: '更改失败', detail, life: configManager.get('ui').toastLife })
  } finally {
    isChangingPassword.value = false
  }
}
</script>
