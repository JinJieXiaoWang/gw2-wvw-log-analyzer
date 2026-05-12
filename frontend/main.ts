/**
 * 应用入口
 * 功能：初始化 Vue 应用、注册插件和全局组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 * 更新：2026-05-12 - 修复 PrimeVue v4 样式加载顺序与配置冲突
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

// =============================================================================
// 1. 样式引入 (顺序至关重要)
// 规则：所有样式通过 index.css 统一聚合引入，main.ts 中仅保留唯一入口
// =============================================================================

import './styles/index.css'
import 'virtual:svg-icons-register'

// =============================================================================
// 2. 插件与服务引入
// =============================================================================

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'

import { permissionDirective } from './directive/permission'
import { ThemeService } from './services/system/themeService'
import { GameThemePreset } from './config/themePreset'
import { authStore } from './composables/system/usePermission'
import { startTokenMonitor, clearToken } from './utils/auth/tokenManager'

// 在创建应用前初始化主题系统
ThemeService.initialize()

const app = createApp(App)

// =============================================================================
// 3. PrimeVue 配置 (v4 标准化写法)
// =============================================================================

app.use(PrimeVue, {
  ripple: true,
  // v4 中 inputStyle/variant 已废弃，统一在 theme.options 中配置
  theme: {
    preset: GameThemePreset, // 使用你的自定义预设
    options: {
      prefix: 'p',
      darkModeSelector: ':root', // 强制深色模式
      // 如果需要全局控制输入框样式，在此处添加 cssLayer 或其他配置
    }
  }
})

app.use(ToastService)
app.use(ConfirmationService)
app.use(pinia)
app.use(router)

// 注册全局指令
app.directive('permission', permissionDirective)
app.directive('tooltip', Tooltip)

// =============================================================================
// 4. 认证事件处理
// =============================================================================

/**
 * 处理认证过期/登出事件
 */
window.addEventListener('auth:logout', (event) => {
  // 类型安全处理
  const detail = (event as CustomEvent).detail || {}
  const source = detail.source || 'unknown'

  // 清除认证状态
  authStore.clearAuth()
  clearToken()

  const currentRoute = router.currentRoute.value

  // 触发全局 Toast
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

  // 只有需要认证的页面才跳转
  const requiresAuth = currentRoute.meta?.requiresAuth !== false
  if (requiresAuth && currentRoute.path !== '/login') {
    sessionStorage.setItem('auth_redirect', currentRoute.fullPath)
    router.push('/login')
  }
})

/**
 * 处理登录成功事件
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
// 5. Token 监控启动
// =============================================================================

startTokenMonitor(() => {
  const currentRoute = router.currentRoute.value
  const requiresAuth = currentRoute.meta?.requiresAuth !== false
  
  if (requiresAuth) {
    window.dispatchEvent(new CustomEvent('auth:logout', {
      detail: { source: 'token_monitor' }
    }))
  } else {
    authStore.clearAuth()
    clearToken()
  }
}, 60000)

// =============================================================================
// 6. 应用挂载
// =============================================================================

app.mount('#app')