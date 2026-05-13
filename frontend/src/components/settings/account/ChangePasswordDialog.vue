<template>
  <BaseDialog
    :visible="visible"
    header="更改密码"
    modal
    :closable="!isChangingPassword"
    :close-on-escape="!isChangingPassword"
    width="28rem"
    :destroy-on-hide="true"
    confirm-label="确认更改"
    confirm-icon="pi pi-check"
    confirm-severity="primary"
    cancel-label="取消"
    :loading="isChangingPassword"
    :confirm-disabled="!canSubmit"
    @confirm="handleChangePassword"
  >
    <div class="space-y-4 pt-2">
      <FormField label="当前密码">
        <Password
          v-model="passwordForm.oldPassword"
          :feedback="false"
          toggle-mask
          placeholder="请输入当前密码"
          class="w-full"
          :input-class="'w-full'"
          @keydown.enter="handleChangePassword"
        />
      </FormField>
      <FormField
        label="新密码"
        hint="密码长度至少8位，需包含大小写字母和数字"
      >
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
      </FormField>
      <FormField
        label="确认新密码"
        :error="confirmPasswordError"
      >
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
      </FormField>
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
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import FormField from '@/components/common/ui/input/FormField.vue'
import Password from 'primevue/password'
import { authService } from '@/services/auth/authService'
import { authStore } from '@/composables/system/usePermission'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [boolean]
  success: []
}>()

const toast = useToast()
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
  try {
    const result = await authService.changePassword(payload)
    const isSuccess = result?.success === true || (result?.code >= 200 && result?.code < 300)
    if (isSuccess) {
      toast.add({ severity: 'success', summary: '密码已更改', detail: '请使用新密码重新登录', life: 3000 })
      emit('update:visible', false)
      emit('success')
      resetPasswordForm()
    } else {
      toast.add({ severity: 'error', summary: '更改失败', detail: result?.message || result?.msg || '请检查当前密码是否正确', life: 3000 })
    }
  } catch (error: any) {
    const detail = error?.response?.data?.message || error?.response?.data?.msg || error?.message || '网络异常，请稍后重试'
    toast.add({ severity: 'error', summary: '更改失败', detail, life: 3000 })
  } finally {
    isChangingPassword.value = false
  }
}

onUnmounted(() => {
  resetPasswordForm()
  isChangingPassword.value = false
})
</script>
