/**
 * 全局权限守卫 Composable
 * 功能：提供页面级和按钮级的统一权限检查
 * 使用场景：需要在运行时动态检查权限的组件
 */

import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePermission } from '@/composables/system/usePermission'
import { authStore } from '@/composables/system/usePermission'

export function useAuthGuard() {
  const route = useRoute()
  const router = useRouter()
  const { isAuthenticated, can, isAdmin } = usePermission()

  /**
   * 检查当前页面权限
   * @returns 是否有权访问当前页面
   */
  const hasPagePermission = computed(() => {
    const requiresAuth = route.meta.requiresAuth as boolean
    if (!requiresAuth) {
      return true
    }
    if (!isAuthenticated.value) {
      return false
    }
    const requiredPermissions = route.meta.permissions as string[] || []
    if (requiredPermissions.length === 0) {
      return true
    }
    return requiredPermissions.some(p => can(p as any))
  })

  /**
   * 强制要求认证，未登录则跳转登录页并记录重定向路径
   */
  const requireAuth = (): boolean => {
    if (isAuthenticated.value) {
      return true
    }
    sessionStorage.setItem('auth_redirect', route.fullPath)
    router.push('/login')
    return false
  }

  /**
   * 检查是否需要显示操作按钮（已登录即可，不检查具体权限）
   */
  const canOperate = computed(() => isAdmin.value)

  /**
   * 检查是否可上传
   */
  const canUpload = computed(() => can('upload'))

  /**
   * 检查是否可写入/修改
   */
  const canWrite = computed(() => can('write'))

  /**
   * 检查是否可删除
   */
  const canDelete = computed(() => can('delete'))

  /**
   * 检查是否可管理用户（仅 super_admin）
   */
  const canManageUsers = computed(() => can('manage_users'))

  return {
    hasPagePermission,
    requireAuth,
    canOperate,
    canUpload,
    canWrite,
    canDelete,
    canManageUsers,
    isAuthenticated,
    isAdmin
  }
}

export { authStore }
