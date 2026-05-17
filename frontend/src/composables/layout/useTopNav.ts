import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authStore, usePermission } from '@/composables/system/usePermission'
import { filterMenusByPermission } from '@/utils/menu/menuAdapter'
import { menuItems as fallbackMenuItems } from '@/layout/components/topNav/menuConfig'

export function useTopNav() {
  const router = useRouter()
  const { can } = usePermission()

  const searchQuery = ref('')
  const showUserMenu = ref(false)
  const mobileMenuOpen = ref(false)
  const showLogoutConfirmDialog = ref(false)
  const isLoggingOut = ref(false)

  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const isOperator = computed(() => authStore.currentRole === 'operator' || authStore.currentRole === 'super_admin')
  const user = computed(() => authStore.currentUser)
  const userInitial = computed(() => user.value?.username?.charAt(0).toUpperCase() || 'A')
  const canWrite = computed(() => can('write'))

  const currentPath = computed(() => router.currentRoute.value.path)

  /** 递归转换后端菜单格式 → 前端 AppMenuItem 格式 */
  function convertMenuItem(m: any): any {
    const converted: any = {
      path: m.path || '',
      label: m.menu_name || m.label || '',
      icon: m.icon ? `pi pi-${m.icon}` : (m.icon || 'pi pi-circle'),
      description: m.remark || m.description || '',
      requireAuth: !!m.perms,
      perms: m.perms || '',
    }
    if (m.children && m.children.length > 0) {
      converted.children = m.children.map(convertMenuItem)
    }
    return converted
  }

  /** 统一菜单数据：后端菜单优先，否则使用备用配置 */
  const menuData = computed(() => {
    const menus = authStore.menus?.length > 0
      ? authStore.menus.map(convertMenuItem)
      : fallbackMenuItems
    return filterMenusByPermission(menus, (perm: string) => can(perm as any), isAuthenticated.value)
  })

  const handleSearch = () => {
    if (searchQuery.value.trim()) {
      router.push({ path: '/logs', query: { search: searchQuery.value.trim() } })
    }
  }

  const handleLogout = async () => {
    isLoggingOut.value = true
    try {
      await authStore.logout()
      router.push('/')
    } finally {
      isLoggingOut.value = false
      showLogoutConfirmDialog.value = false
    }
  }

  const handleNavigate = (path: string) => {
    if (path) router.push(path)
  }

  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement
    if (!target.closest('.user-dropdown') && !target.closest('.user-menu-trigger')) {
      showUserMenu.value = false
    }
  }

  return {
    searchQuery,
    showUserMenu,
    mobileMenuOpen,
    showLogoutConfirmDialog,
    isLoggingOut,
    isAuthenticated,
    isOperator,
    user,
    userInitial,
    canWrite,
    currentPath,
    menuData,
    handleSearch,
    handleLogout,
    handleNavigate,
    handleClickOutside,
  }
}
