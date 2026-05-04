/**
 * 应用入口
 * 功能：初始化 Vue 应用、注册插件和全局组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 * 更新：2026-04-29 - 集成优化的游戏风格主题预设
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

// 监听认证过期事件
window.addEventListener('auth:logout', () => {
  // 清除认证状态（使用活跃的 AuthStore）
  authStore.clearAuth()
  // 跳转到登录页
  if (router.currentRoute.value.path !== '/login') {
    router.push('/login')
  }
})

app.mount('#app')