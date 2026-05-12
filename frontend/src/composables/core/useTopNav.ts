import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { authStore, usePermission } from '@/composables/system/usePermission'
import { configManager } from '@/services/core/configManager'

export interface MenuItem {
  path: string
  label: string
  icon: string
  description?: string
  requireAuth?: boolean
}

const MENU_ITEMS: MenuItem[] = [
  { path: '/', label: '数据看板', icon: 'pi pi-chart-line', description: '可视化数据' },
  { path: '/logs', label: '日志管理', icon: 'pi pi-file', description: '解析与管理' },
  { path: '/attendance', label: '出勤统计', icon: 'pi pi-users', description: '团队数据' },
  { path: '/skill-analysis', label: '技能循环', icon: 'pi pi-sync', description: '循环分析' },
  { path: '/builds', label: '配置图书馆', icon: 'pi pi-book', description: '战场配置百科' },
  { path: '/build-parser', label: 'Build解析', icon: 'pi pi-code', description: '配置分析' },
  { path: '/settings', label: '系统设置', icon: 'pi pi-cog', description: '系统配置', requireAuth: true }
]

export function useTopNav() {
  const router = useRouter()
  const toast = useToast()
  const { can } = usePermission()

  const searchQuery = ref('')
  const mobileMenuOpen = ref(false)
  const showLogoutConfirmDialog = ref(false)
  const isLoggingOut = ref(false)

  const visibleMenuItems = computed(() => MENU_ITEMS.filter(item => !item.requireAuth || can('write')))
  const currentPath = computed(() => router.currentRoute.value.path)
  const isAuthenticated = computed(() => authStore.isAuthenticated)

  const isActive = (path: string) => {
    if (path === '/') return currentPath.value === '/' || currentPath.value === '/dashboard'
    return currentPath.value.startsWith(path)
  }

  const toggleMobileMenu = () => { mobileMenuOpen.value = !mobileMenuOpen.value }

  const handleSearch = () => {
    if (searchQuery.value.trim()) {
      toast.add({ severity: 'info', summary: '搜索功能', detail: `正在搜索: ${searchQuery.value}`, life: configManager.get('ui').toastLife })
    }
  }

  const handleLogout = async () => {
    isLoggingOut.value = true
    try {
      await authStore.logout()
      toast.add({ severity: 'success', summary: '登出成功', detail: '您已成功退出登录', life: configManager.get('ui').toastLife })
      router.push('/')
    } catch (error) {
      console.error('登出失败:', error)
      toast.add({ severity: 'error', summary: '登出失败', detail: '请稍后重试', life: configManager.get('ui').toastLife })
    } finally {
      isLoggingOut.value = false
      showLogoutConfirmDialog.value = false
    }
  }

  return {
    searchQuery, mobileMenuOpen, showLogoutConfirmDialog, isLoggingOut,
    visibleMenuItems, isAuthenticated,
    isActive, toggleMobileMenu, handleSearch, handleLogout
  }
}
