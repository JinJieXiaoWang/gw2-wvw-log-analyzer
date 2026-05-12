<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center px-4 sm:px-6 lg:px-8">
    <LoginTransitionOverlay
      :visible="showTransitionOverlay"
      :is-loading="isLoading"
      :progress="transitionProgress"
    />

    <div class="hidden lg:block absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" />
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
          WVW战场日志
        </h1>
        <p class="text-gray-400 text-sm sm:text-base">
          公会内部数据管理系统
        </p>
      </div>

      <div class="bg-slate-800/80 backdrop-blur-xl rounded-2xl p-6 sm:p-8 lg:p-10 shadow-2xl border border-slate-700/50 lg:shadow-[0_0_60px_rgba(239,68,68,0.1),0_0_60px_rgba(59,130,246,0.1)] animate-slide-up">
        <div class="text-center mb-6 sm:mb-8">
          <h2 class="text-xl sm:text-2xl font-semibold text-white mb-2">
            操作员登录
          </h2>
          <p class="text-gray-400 text-sm">
            普通成员可直接浏览，无需登录
          </p>
        </div>

        <LoginForm
          :form="loginForm"
          :errors="errors"
          :loading="isLoading"
          :is-valid="isFormValid"
          :remaining-attempts="remainingAttempts"
          @submit="handleLogin"
          @validate-username="validateUsername"
          @validate-password="validatePassword"
          @clear-error="clearError"
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
            返回首页浏览
          </button>
        </div>
      </div>

      <div class="text-center mt-6 sm:mt-8 text-gray-500 text-xs sm:text-sm">
        <p class="mb-1">
          系统采用JWT认证，令牌有效期2小时
        </p>
        <p>同一账户5分钟内最多尝试5次登录</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { authStore } from '@/composables/system/usePermission'
import LoginTransitionOverlay from './LoginTransitionOverlay.vue'
import LoginForm from './LoginForm.vue'

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
const remainingAttempts = ref(5)

const isFormValid = computed(() => loginForm.username.length >= 3 && loginForm.password.length >= 6)

function validateUsername() {
  if (!loginForm.username) errors.username = '请输入用户名'
  else if (loginForm.username.length < 3) errors.username = '用户名至少3个字符'
  else delete errors.username
}

function validatePassword() {
  if (!loginForm.password) errors.password = '请输入密码'
  else if (loginForm.password.length < 6) errors.password = '密码至少6个字符'
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
    transitionProgress.value = Math.min(transitionProgress.value + 5, 90)
  }, 100)

  try {
    const result = await authStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password,
    })
    if (result.success) {
        transitionProgress.value = 100
        loginSuccess.value = '登录成功！正在跳转...'
        
        // 获取登录前保存的重定向路径
        const redirectPath = sessionStorage.getItem('auth_redirect')
        
        // 清除保存的重定向路径
        sessionStorage.removeItem('auth_redirect')
        
        // 跳转到重定向路径或首页
        const targetPath = redirectPath || '/'
        setTimeout(() => router.push(targetPath), 800)
      } else {
      clearInterval(progressInterval)
      showTransitionOverlay.value = false
      errorType.value = (result as any).errorType || 'error'
      loginError.value = result.message || '登录失败'
      if ((result as any).remainingAttempts !== undefined) remainingAttempts.value = (result as any).remainingAttempts
    }
  } catch {
    clearInterval(progressInterval)
    showTransitionOverlay.value = false
    loginError.value = '网络错误，请稍后重试'
  } finally {
    clearInterval(progressInterval)
    isLoading.value = false
  }
}

function goHome() {
  router.push('/')
}
</script>

<style scoped>@import './LoginView.css';</style>
