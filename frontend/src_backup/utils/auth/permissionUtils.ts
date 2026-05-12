/**
 * 权限验证工具
 * 功能：提供权限检查的工具函数
 * 作者：System
 * 创建日期：2024-01-15
 */

import type { Permission } from '@/types/permission'
import { authStore } from '@/composables/system/usePermission'
import { PERMISSION_DESCRIPTIONS } from '@/types/permission'

export function hasPermission(permission: Permission): boolean {
  return authStore.hasPermission(permission)
}

export function hasAllPermissions(permissions: Permission[]): boolean {
  return authStore.hasAllPermissions(permissions)
}

export function hasAnyPermission(permissions: Permission[]): boolean {
  return authStore.hasAnyPermission(permissions)
}

export function isAuthenticated(): boolean {
  return authStore.isAuthenticated
}

export function isAdmin(): boolean {
  return authStore.currentRole === 'super_admin'
}

export function isGuest(): boolean {
  return !authStore.isAuthenticated
}

export function getPermissionDescription(permission: Permission): string {
  return PERMISSION_DESCRIPTIONS[permission] || permission
}

export function getRequiredPermissionsMessage(permissions: Permission[]): string {
  if (permissions.length === 0) {
    return ''
  }

  const names = permissions.map(p => getPermissionDescription(p))
  if (names.length === 1) {
    return `此操作需要${names[0]}权限`
  }

  const last = names.pop()
  return `此操作需要${names.join('、')}和${last}权限`
}

export function canPerformAction(action: Permission): boolean {
  return authStore.hasPermission(action)
}

export function checkPermissionOrThrow(permission: Permission, message?: string): void {
  if (!authStore.hasPermission(permission)) {
    throw new Error(message || `权限不足：需要${getPermissionDescription(permission)}权限`)
  }
}