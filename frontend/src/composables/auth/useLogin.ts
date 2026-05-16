import { reactive, ref, computed, onUnmounted } from 'vue'
import { authStore } from '@/composables/system/usePermission'

export function useLogin() {
  const loginForm = reactive({ username: '', password: '' })
  const errors = reactive({ username: '', password: '' })
  const isLoading = ref(false)
  const loginError = ref('')
  const loginSuccess = ref('')
  const errorType = ref<'error' | 'warning'>('error')
  const remainingAttempts = ref(5)
  const showTransitionOverlay = ref(false)
  const transitionProgress = ref(0)
  let progressInterval: ReturnType<typeof setInterval> | null = null

  const isFormValid = computed(() =>
    loginForm.username.length >= 3 && loginForm.username.length <= 50 &&
    loginForm.password.length >= 8 && loginForm.password.length <= 128 &&
    !errors.username && !errors.password
  )

  const validateUsername = () => {
    const u = loginForm.username.trim()
    errors.username = !u ? '请输入用户名' : u.length < 3 ? '用户名长度不能少于3个字符' : u.length > 50 ? '用户名长度不能超过50个字符' : ''
  }

  const validatePassword = () => {
    const p = loginForm.password
    errors.password = !p ? '请输入密码' : p.length < 8 ? '密码长度不能少于8个字符' : p.length > 128 ? '密码长度不能超过128个字符' : ''
  }

  const clearError = (field: 'username' | 'password') => {
    errors[field] = ''
    loginError.value = ''
  }

  const startTransitionProgress = () => {
    transitionProgress.value = 0
    if (progressInterval) clearInterval(progressInterval)
    progressInterval = setInterval(() => {
      transitionProgress.value += 2
      if (transitionProgress.value >= 100) {
        transitionProgress.value = 100
        if (progressInterval) { clearInterval(progressInterval); progressInterval = null }
      }
    }, 20)
  }

  const handleLogin = async () => {
    loginError.value = ''
    loginSuccess.value = ''
    validateUsername()
    validatePassword()
    if (!isFormValid.value) return

    isLoading.value = true
    try {
      const result = await authStore.login({ username: loginForm.username.trim(), password: loginForm.password })
      if (result.success) {
        showTransitionOverlay.value = true
        loginSuccess.value = result.message
        errorType.value = 'error'
        startTransitionProgress()
        setTimeout(() => {
          if (progressInterval) clearInterval(progressInterval)
          window.dispatchEvent(new CustomEvent('auth:login'))
        }, 1000)
      } else {
        loginError.value = result.message
        if (result.error_code === 'INVALID_CREDENTIALS') { errorType.value = 'error'; remainingAttempts.value = Math.max(0, remainingAttempts.value - 1) }
        else if (result.message.includes('锁定')) { errorType.value = 'warning'; remainingAttempts.value = 0 }
        else { errorType.value = 'error'; remainingAttempts.value = Math.max(0, remainingAttempts.value - 1) }
      }
    } catch (error: unknown) {
      const err = error as { response?: { status?: number; data?: { message?: string } } }
      if (!navigator.onLine) loginError.value = '网络已断开，请检查网络连接后重试'
      else if ((err.response?.status || 0) >= 500) loginError.value = '服务器繁忙，请稍后再试'
      else if (err.response?.status === 429) loginError.value = '请求过于频繁，请稍后再试'
      else loginError.value = err.response?.data?.message || '登录失败，请检查账号密码后重试'
      errorType.value = 'error'
      console.error('Login error:', error)
    } finally {
      isLoading.value = false
    }
  }

  onUnmounted(() => { if (progressInterval) { clearInterval(progressInterval); progressInterval = null } })

  return { loginForm, errors, isLoading, loginError, loginSuccess, errorType, remainingAttempts, showTransitionOverlay, transitionProgress, isFormValid, validateUsername, validatePassword, clearError, handleLogin }
}
