<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center px-4 sm:px-6 lg:px-8">
    <!-- 过渡遮罩层 -->
    <transition name="fade">
      <div
        v-if="showTransitionOverlay"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/95 backdrop-blur-md"
      >
        <div class="text-center animate-bounce-in">
          <div class="w-24 h-24 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30 animate-pulse">
            <span class="text-5xl">⚔️</span>
          </div>
          <h2 class="text-2xl font-bold text-white mb-2">
            登录成功
          </h2>
          <p class="text-gray-400">
            正在跳转至首页...
          </p>
          <div class="mt-6 flex justify-center">
            <div class="w-64 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-blue-500 to-blue-700 rounded-full transition-all duration-1000 ease-out"
                :style="{ width: transitionProgress + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- PC端背景装饰 -->
    <div class="hidden lg:block absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" />
      <div
        class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"
        style="animation-delay: 1s;"
      />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/5 rounded-full" />
    </div>

    <div class="relative z-10 w-full max-w-md sm:max-w-lg lg:max-w-xl animate-fade-in">
      <!-- 品牌区域 -->
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

      <!-- 登录卡片 -->
      <div class="bg-slate-800/80 backdrop-blur-xl rounded-2xl p-6 sm:p-8 lg:p-10 shadow-2xl border border-slate-700/50 lg:shadow-[0_0_60px_rgba(239,68,68,0.1),0_0_60px_rgba(59,130,246,0.1)] animate-slide-up">
        <!-- 标题区域 -->
        <div class="text-center mb-6 sm:mb-8">
          <h2 class="text-xl sm:text-2xl font-semibold text-white mb-2">
            操作员登录
          </h2>
          <p class="text-gray-400 text-sm">
            普通成员可直接浏览，无需登录
          </p>
        </div>

        <!-- 登录表单 -->
        <form
          class="space-y-5 sm:space-y-6"
          @submit.prevent="handleLogin"
        >
          <!-- 用户名输入 -->
          <div>
            <label class="block text-gray-300 text-sm font-medium mb-2 sm:mb-3">用户名</label>
            <input
              v-model="loginForm.username"
              type="text"
              placeholder="请输入用户名"
              class="w-full px-4 py-3 sm:px-5 sm:py-3.5 lg:px-6 lg:py-4 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base sm:text-lg"
              :class="errors.username ? 'border-red-500' : 'border-slate-600'"
              @blur="validateUsername"
              @input="clearError('username')"
            >
            <div
              v-if="errors.username"
              class="mt-2 sm:mt-3"
            >
              <span class="text-red-400 text-sm sm:text-base">{{ errors.username }}</span>
            </div>
            <div
              v-else-if="loginForm.username"
              class="mt-2 sm:mt-3"
            >
              <span class="text-green-400 text-xs sm:text-sm">✓ 用户名格式正确</span>
            </div>
          </div>

          <!-- 密码输入 -->
          <div>
            <label class="block text-gray-300 text-sm font-medium mb-2 sm:mb-3">密码</label>
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              class="w-full px-4 py-3 sm:px-5 sm:py-3.5 lg:px-6 lg:py-4 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base sm:text-lg"
              :class="errors.password ? 'border-red-500' : 'border-slate-600'"
              @blur="validatePassword"
              @input="clearError('password')"
            >
            <div
              v-if="errors.password"
              class="mt-2 sm:mt-3"
            >
              <span class="text-red-400 text-sm sm:text-base">{{ errors.password }}</span>
            </div>
            <div
              v-else-if="loginForm.password"
              class="mt-2 sm:mt-3"
            >
              <span class="text-green-400 text-xs sm:text-sm">✓ 密码格式正确</span>
            </div>
          </div>

          <!-- 登录限流提示 -->
          <div
            v-if="remainingAttempts > 0"
            class="flex items-center gap-2 text-gray-500 text-xs sm:text-sm"
          >
            <i class="pi pi-shield text-blue-400" />
            <span>剩余登录尝试次数: <span class="text-blue-400 font-medium">{{ remainingAttempts }}</span> / 5</span>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="w-full py-3 sm:py-4 px-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 text-base sm:text-lg shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
          >
            <svg
              v-if="isLoading"
              class="animate-spin h-5 w-5 sm:h-6 sm:w-6"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
                fill="none"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>{{ isLoading ? '登录中...' : '登 录' }}</span>
          </button>
        </form>

        <!-- 错误提示 -->
        <transition name="slide-down">
          <div
            v-if="loginError"
            class="mt-5 sm:mt-6 p-4 sm:p-5 rounded-xl border"
            :class="errorType === 'warning' ? 'bg-yellow-900/20 border-yellow-700/50' : 'bg-red-900/20 border-red-700/50'"
          >
            <div class="flex items-start gap-3">
              <i
                v-if="errorType === 'warning'"
                class="pi pi-warning-circle text-yellow-400 mt-0.5 flex-shrink-0 text-lg sm:text-xl"
              />
              <i
                v-else
                class="pi pi-exclamation-circle text-red-400 mt-0.5 flex-shrink-0 text-lg sm:text-xl"
              />
              <p
                class="text-sm sm:text-base"
                :class="errorType === 'warning' ? 'text-yellow-400' : 'text-red-400'"
              >
                {{ loginError }}
              </p>
            </div>
          </div>
        </transition>

        <!-- 成功提示 -->
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

        <!-- 返回首页 -->
        <div class="mt-6 sm:mt-8 text-center">
          <button
            class="text-gray-400 hover:text-white text-sm sm:text-base underline underline-offset-4 transition-colors"
            @click="goHome"
          >
            返回首页浏览
          </button>
        </div>
      </div>

      <!-- 底部信息 -->
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
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '@/composables/system/usePermission'

const router = useRouter()

const loginForm = reactive({
  username: '',
  password: ''
})

const errors = reactive({
  username: '',
  password: ''
})

const isLoading = ref(false)
const loginError = ref('')
const loginSuccess = ref('')
const errorType = ref<'error' | 'warning'>('error')
const remainingAttempts = ref(5)

// 过渡动画状态
const showTransitionOverlay = ref(false)
const transitionProgress = ref(0)
let progressInterval: ReturnType<typeof setInterval> | null = null

const isFormValid = computed(() => {
  return loginForm.username.length >= 3 && 
         loginForm.username.length <= 50 && 
         loginForm.password.length >= 6 && 
         loginForm.password.length <= 128 &&
         !errors.username && 
         !errors.password
})

const validateUsername = () => {
  const username = loginForm.username.trim()
  if (!username) {
    errors.username = '请输入用户名'
  } else if (username.length < 3) {
    errors.username = '用户名长度不能少于3个字符'
  } else if (username.length > 50) {
    errors.username = '用户名长度不能超过50个字符'
  } else {
    errors.username = ''
  }
}

const validatePassword = () => {
  const password = loginForm.password
  if (!password) {
    errors.password = '请输入密码'
  } else if (password.length < 6) {
    errors.password = '密码长度不能少于6个字符'
  } else if (password.length > 128) {
    errors.password = '密码长度不能超过128个字符'
  } else {
    errors.password = ''
  }
}

const clearError = (field: 'username' | 'password') => {
  errors[field] = ''
  loginError.value = ''
}

const startTransitionProgress = () => {
  transitionProgress.value = 0
  const duration = 1000
  const intervalTime = 20
  const increment = 100 / (duration / intervalTime)
  
  progressInterval = setInterval(() => {
    transitionProgress.value += increment
    if (transitionProgress.value >= 100) {
      transitionProgress.value = 100
      if (progressInterval) {
        clearInterval(progressInterval)
      }
    }
  }, intervalTime)
}

const handleLogin = async () => {
  loginError.value = ''
  loginSuccess.value = ''
  
  validateUsername()
  validatePassword()

  if (!isFormValid.value) {
    return
  }

  isLoading.value = true

  try {
    const result = await authStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password
    })

    if (result.success) {
      // 显示过渡遮罩层
      showTransitionOverlay.value = true
      loginSuccess.value = result.message
      errorType.value = 'error'
      
      // 启动进度条动画
      startTransitionProgress()
      
      // 延迟跳转，让过渡动画完成
      setTimeout(() => {
        if (progressInterval) {
          clearInterval(progressInterval)
        }
        router.push('/')
      }, 1000)
    } else {
      loginError.value = result.message
      
      if (result.error_code === 'INVALID_CREDENTIALS') {
        errorType.value = 'error'
        remainingAttempts.value = Math.max(0, remainingAttempts.value - 1)
      } else if (result.message.includes('锁定')) {
        errorType.value = 'warning'
        remainingAttempts.value = 0
      } else {
        errorType.value = 'error'
        remainingAttempts.value = Math.max(0, remainingAttempts.value - 1)
      }
    }
  } catch (error) {
    loginError.value = '网络异常，请检查网络连接后重试'
    errorType.value = 'error'
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  // 页面加载时添加入场动画
  document.body.classList.add('login-page-loaded')
})
</script>

<style scoped>
/* 页面入场动画 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片滑入动画 */
.animate-slide-up {
  animation: slideUp 0.5s ease-out 0.2s forwards;
  opacity: 0;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 弹入动画 */
.animate-bounce-in {
  animation: bounceIn 0.5s ease-out forwards;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 淡入淡出过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 下滑过渡 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 页面加载过渡 */
.login-page-loaded {
  transition: background-color 0.5s ease;
}
</style>