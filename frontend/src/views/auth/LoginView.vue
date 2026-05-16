<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center px-4 sm:px-6 lg:px-8">
    <LoginTransitionOverlay
      :visible="showTransitionOverlay"
      :is-loading="isLoading"
      :progress="transitionProgress"
    />

    <div class="hidden lg:block absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" />
      <!-- 动态值，无法使用 Tailwind 静态类 -->
      <div
        class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"
        style="animation-delay: 1s;"
      />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/5 rounded-full" />
    </div>

    <div class="relative z-10 w-full max-w-md sm:max-w-lg lg:max-w-xl animate-fade-in">
      <div class="text-center mb-8 sm:mb-10">
        <div class="inline-flex items-center justify-center w-20 h-20 sm:w-24 sm:h-24 bg-slate-800/80 backdrop-blur-xl rounded-2xl mb-4 sm:mb-6 shadow-lg shadow-blue-500/25 border border-slate-700/50">
          <img
            src="@/assets/fonts/logo.png"
            alt="GW2 Logo"
            class="w-16 h-16 sm:w-20 sm:h-20 object-contain"
          >
        </div>
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2 sm:mb-3">
          {{ PAGE_TITLE }}
        </h1>
        <p class="text-gray-400 text-sm sm:text-base">
          {{ PAGE_SUBTITLE }}
        </p>
      </div>

      <div class="bg-slate-800/80 backdrop-blur-xl rounded-2xl p-6 sm:p-8 lg:p-10 shadow-2xl border border-slate-700/50 lg:shadow-[0_0_60px_rgba(239,68,68,0.1),0_0_60px_rgba(59,130,246,0.1)] animate-slide-up">
        <div class="text-center mb-6 sm:mb-8">
          <h2 class="text-xl sm:text-2xl font-semibold text-white mb-2">
            {{ LOGIN_TITLE }}
          </h2>
          <p class="text-gray-400 text-sm">
            {{ LOGIN_SUBTITLE }}
          </p>
        </div>

        <LoginForm
          :form-state="{ form: loginForm, errors }"
          :submit-status="{ loading: isLoading, isValid: isFormValid, remainingAttempts }"
          @submit="handleLogin"
          @validate-username="validateUsername"
          @validate-password="validatePassword"
          @clear-error="clearError"
          @update:form="updateLoginForm"
        />

        <transition name="slide-down">
          <div
            v-if="loginError"
            class="mt-5 sm:mt-6 p-4 sm:p-5 rounded-xl border"
            :class="errorType === 'warning' ? 'bg-yellow-900/20 border-yellow-700/50' : 'bg-red-900/20 border-red-700/50'"
          >
            <div class="flex items-start gap-3">
              <i
                :class="errorType === 'warning' ? 'pi pi-warning-circle text-yellow-400' : 'pi pi-exclamation-circle text-red-400'"
                class="mt-0.5 flex-shrink-0 text-lg sm:text-xl"
              />
              <p
                :class="errorType === 'warning' ? 'text-yellow-400' : 'text-red-400'"
                class="text-sm sm:text-base"
              >
                {{ loginError }}
              </p>
            </div>
          </div>
        </transition>

        <transition name="slide-down">
          <div
            v-if="loginSuccess"
            class="mt-5 sm:mt-6 p-4 sm:p-5 bg-green-900/20 border border-green-700/50 rounded-xl"
          >
            <div class="flex items-center gap-3">
              <i class="pi pi-check-circle text-green-400 text-lg sm:text-xl" />
              <p class="text-green-400 text-sm sm:text-base">
                {{ loginSuccess }}
              </p>
            </div>
          </div>
        </transition>

        <div class="mt-6 sm:mt-8 text-center">
          <button
            class="text-gray-400 hover:text-white text-sm sm:text-base underline underline-offset-4 transition-colors"
            :disabled="isLoading"
            @click="goHome"
          >
            {{ GO_HOME_TEXT }}
          </button>
        </div>
      </div>

      <div class="text-center mt-6 sm:mt-8 text-gray-500 text-xs sm:text-sm">
        <p class="mb-1">
          {{ JWT_NOTICE }}
        </p>
        <p>{{ RATE_LIMIT_NOTICE }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { authStore } from '@/composables/system/usePermission'
import { useToast } from 'primevue/usetoast'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from './LoginForm.vue'
import LoginTransitionOverlay from './LoginTransitionOverlay.vue'

// ========== 常量定义 ==========

// 页面文案
const PAGE_TITLE = 'WVW战场日志'
const PAGE_SUBTITLE = '公会内部数据管理系统'
const LOGIN_TITLE = '操作员登录'
const LOGIN_SUBTITLE = '普通成员可直接浏览，无需登录'
const GO_HOME_TEXT = '返回首页浏览'
const JWT_NOTICE = '系统采用JWT认证，令牌有效期2小时'
const RATE_LIMIT_NOTICE = '同一账户5分钟内最多尝试5次登录'

// 表单验证文案
const USERNAME_REQUIRED_ERROR = '请输入用户名'
const USERNAME_MIN_LENGTH_ERROR = '用户名至少3个字符'
const PASSWORD_REQUIRED_ERROR = '请输入密码'
const PASSWORD_MIN_LENGTH_ERROR = '密码至少6个字符'

// 登录状态文案
const LOGIN_SUCCESS_MESSAGE = '登录成功！正在跳转...'
const LOGIN_FAILED_DEFAULT_MESSAGE = '登录失败'
const NETWORK_ERROR_MESSAGE = '网络错误，请稍后重试'

// 表单验证阈值
const MIN_USERNAME_LENGTH = 3
const MIN_PASSWORD_LENGTH = 6

// 过渡动画配置
const TRANSITION_STEP = 5
const TRANSITION_MAX_PROGRESS = 90
const TRANSITION_INTERVAL_MS = 100
const REDIRECT_DELAY_MS = 800

// 剩余尝试次数默认值
const DEFAULT_REMAINING_ATTEMPTS = 5

// ========== 逻辑 ==========

const router = useRouter()
const toast = useToast()

const loginForm = reactive({ username: '', password: '' })
const errors = reactive<{ username?: string; password?: string }>({})
const isLoading = ref(false)
const showTransitionOverlay = ref(false)
const transitionProgress = ref(0)
const loginError = ref('')
const loginSuccess = ref('')
const errorType = ref('error')
const remainingAttempts = ref(DEFAULT_REMAINING_ATTEMPTS)

const isFormValid = computed(() => {
  const valid = loginForm.username.length >= MIN_USERNAME_LENGTH && loginForm.password.length >= MIN_PASSWORD_LENGTH
  return valid
})

function updateLoginForm(form: { username: string; password: string }) {
  loginForm.username = form.username
  loginForm.password = form.password
}

function validateUsername() {
  if (!loginForm.username) errors.username = USERNAME_REQUIRED_ERROR
  else if (loginForm.username.length < MIN_USERNAME_LENGTH) errors.username = USERNAME_MIN_LENGTH_ERROR
  else delete errors.username
}

function validatePassword() {
  if (!loginForm.password) errors.password = PASSWORD_REQUIRED_ERROR
  else if (loginForm.password.length < MIN_PASSWORD_LENGTH) errors.password = PASSWORD_MIN_LENGTH_ERROR
  else delete errors.password
}

function clearError(field: string) {
  delete (errors as any)[field]
  loginError.value = ''
}

async function handleLogin() {
  validateUsername()
  validatePassword()
  if (errors.username || errors.password) return

  isLoading.value = true
  showTransitionOverlay.value = true
  transitionProgress.value = 0
  loginError.value = ''

  const progressInterval = setInterval(() => {
    transitionProgress.value = Math.min(transitionProgress.value + TRANSITION_STEP, TRANSITION_MAX_PROGRESS)
  }, TRANSITION_INTERVAL_MS)

  try {
    const result = await authStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password,
    })
    if (result.success) {
        transitionProgress.value = 100
        loginSuccess.value = LOGIN_SUCCESS_MESSAGE

        // 获取登录前保存的重定向路径
        const redirectPath = sessionStorage.getItem('auth_redirect')

        // 清除保存的重定向路径
        sessionStorage.removeItem('auth_redirect')

        // 跳转到重定向路径或首页
        const targetPath = redirectPath || '/'
        setTimeout(() => router.push(targetPath), REDIRECT_DELAY_MS)
      } else {
      clearInterval(progressInterval)
      showTransitionOverlay.value = false
      errorType.value = (result as any).errorType || 'error'
      loginError.value = result.message || LOGIN_FAILED_DEFAULT_MESSAGE
      if ((result as any).remainingAttempts !== undefined) remainingAttempts.value = (result as any).remainingAttempts
    }
  } catch {
    clearInterval(progressInterval)
    showTransitionOverlay.value = false
    loginError.value = NETWORK_ERROR_MESSAGE
  } finally {
    clearInterval(progressInterval)
    isLoading.value = false
  }
}

function goHome() {
  router.push('/')
}
</script>

<style scoped>@import '@/styles/views/auth/LoginView.css';</style>
