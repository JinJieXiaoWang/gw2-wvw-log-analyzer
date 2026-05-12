/**
 * 权限路由守卫
 * 功能：保护需要特定权限的路由
 * 作者：System
 * 创建日期：2024-01-15
 */

import type { RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import { authStore } from '@/composables/system/usePermission'
import type { Permission } from '@/types/permission'
import { apiFactory } from '@/services/core/apiService'

export async function permissionGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
): Promise<void> {
  const requiresAuth = to.meta.requiresAuth
  const isAuthenticated = authStore.isAuthenticated

  // 公开页面直接访问
  if (to.meta.public) {
    next()
    return
  }

  // 需要认证的页面
  if (requiresAuth) {
    if (!isAuthenticated) {
      next('/login')
      return
    }

    // 检查权限
    const permissions = (to.meta.permissions as Permission[]) || []
    if (permissions.length > 0 && !authStore.hasAnyPermission(permissions)) {
      next('/')
      return
    }
  }

  next()
}

export async function checkLoginStatus(): Promise<boolean> {
  try {
    const result = await apiFactory.get<any>('/api/v1/auth/status')
    return result.success && result.data?.is_authenticated
  } catch (error) {
    console.error('Failed to check login status:', error)
    return false
  }
}