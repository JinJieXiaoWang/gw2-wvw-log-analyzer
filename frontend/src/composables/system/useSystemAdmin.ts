import { SESSION_TIMEOUT_OPTIONS } from '@/constants/options'
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { authStore } from '@/composables/system/usePermission'
import { configManager } from '@/services/core/configManager'
import { STORAGE_KEYS } from '@/config/storage.config'

export function useSystemAdmin() {
  const toast = useToast()
  const activeSection = ref('account')
  const isSaving = ref(false)
  const accountErrors = ref('')

  const adminSections = [
    { id: 'account', label: '账号管理', icon: 'pi pi-user' },
    { id: 'security', label: '安全设置', icon: 'pi pi-shield' },
    { id: 'system', label: '系统信息', icon: 'pi pi-info-circle' }
  ]

  const sessionTimeoutOptions = SESSION_TIMEOUT_OPTIONS

  const sessionTimeout = ref(60)

  const accountForm = reactive({ username: '', newPassword: '', confirmPassword: '' })

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

  const lastLoginTime = computed(() => {
    const user = authStore.currentUser
    return user?.loginTime ? new Date(user.loginTime).toLocaleString('zh-CN') : 'δ֪'
  })

  const saveAccount = async () => {
    accountErrors.value = ''
    if (!accountForm.username || accountForm.username.length < 3) { accountErrors.value = '用户名长度至少3个字符'; return }
    if (accountForm.newPassword) {
      const validation = authStore.validatePassword(accountForm.newPassword)
      if (!validation.valid) { accountErrors.value = validation.errors.join('；'); return }
      if (accountForm.newPassword !== accountForm.confirmPassword) { accountErrors.value = '两次输入的密码不一致'; return }
    }
    isSaving.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      if (accountForm.newPassword) {
        const result = authStore.setAdminConfig(accountForm.username, accountForm.newPassword)
        if (!result.success) { accountErrors.value = result.message; return }
      } else {
        // 安全修复：不再在 localStorage 中存储密码
        localStorage.setItem(STORAGE_KEYS.ADMIN_CONFIG, JSON.stringify({ username: accountForm.username }))
      }
      toast.add({ severity: 'success', summary: '保存成功', detail: '管理员账号配置已更新', life: configManager.get('ui').toastLife })
      accountForm.newPassword = ''; accountForm.confirmPassword = ''
    } catch {
      toast.add({ severity: 'error', summary: '保存失败', detail: '发生错误，请稍后重试', life: configManager.get('ui').toastLife })
    } finally { isSaving.value = false }
  }

  const resetAccountForm = () => {
    const config = authStore.getAdminConfig()
    accountForm.username = config.username
    accountForm.newPassword = ''
    accountForm.confirmPassword = ''
    accountErrors.value = ''
  }

  onMounted(() => {
    if (!authStore.isAuthenticated || (authStore.currentRole !== 'super_admin' && authStore.currentRole !== 'operator')) return
    resetAccountForm()
  })

  return { activeSection, isSaving, accountErrors, adminSections, sessionTimeoutOptions, sessionTimeout, accountForm, passwordValidation, lastLoginTime, saveAccount, resetAccountForm }
}
