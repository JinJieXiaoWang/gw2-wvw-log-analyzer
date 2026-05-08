/**
 * 应用入口
 * 功能：初始化 Vue 应用、注册插件和全局组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 * 更新：2026-05-07 - 集成权限控制系统（Token监控、智能跳转）
 */

import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

import App from './App.vue'
import router from './router'
import pinia from './store'
import { permissionDirective } from './directive/permission'
import { ThemeService } from './services/system/themeService'
import { GameThemePreset } from './config/themePreset'
import { authStore } from './composables/system/usePermission'
import { startTokenMonitor, clearToken } from './utils/auth/tokenManager'
import './styles/index.css'

// 在创建应用前初始化主题系统
ThemeService.initialize()

const app = createApp(App)

app.use(PrimeVue
  , {
    ripple: true,
    inputStyle: 'filled',
    inputVariant: 'filled',
    theme: {
      preset: GameThemePreset,
      options: {
        darkModeSelector: ':root'
      }
    }
  }
)
app.use(ToastService)
app.use(ConfirmationService)
app.use(pinia)
app.use(router)

app.directive('permission', permissionDirective)

// =============================================================================
// 认证事件处理
// =============================================================================

/**
 * 处理认证过期/登出事件
 * - 公开页面：清除状态 + Toast 提示，不跳转
 * - 认证页面：清除状态 + 跳转登录页
 */
window.addEventListener('auth:logout', (event: Event) => {
  const customEvent = event as CustomEvent
  const source = customEvent.detail?.source || 'unknown'

  // 清除认证状态
  authStore.clearAuth()
  clearToken()

  const currentRoute = router.currentRoute.value

  // 触发全局 Toast 事件（由 App.vue 消费）
  if (source === 'api') {
    window.dispatchEvent(new CustomEvent('global:toast', {
      detail: {
        severity: 'warn',
        summary: '登录已过期',
        message: '您的登录状态已过期，请重新登录',
        life: 5000
      }
    }))
  }

  // 登录过期一律跳转登录页（除非已在登录页）
  if (currentRoute.path !== '/login') {
    sessionStorage.setItem('auth_redirect', currentRoute.fullPath)
    router.push('/login')
  }
})

/**
 * 处理登录成功事件
 * - 检查 sessionStorage 中是否有重定向路径
 * - 有则跳转回原页面，无则跳转首页
 */
window.addEventListener('auth:login', () => {
  const redirectPath = sessionStorage.getItem('auth_redirect')
  sessionStorage.removeItem('auth_redirect')
  if (redirectPath && redirectPath !== '/login') {
    router.push(redirectPath)
  } else {
    router.push('/')
  }
})

// =============================================================================
// Token 过期监控启动
// =============================================================================

startTokenMonitor(() => {
  // Token 过期时触发登出事件
  window.dispatchEvent(new CustomEvent('auth:logout', {
    detail: { source: 'token_monitor' }
  }))
}, 60000) // 每 60 秒检测一次

app.mount('#app')
