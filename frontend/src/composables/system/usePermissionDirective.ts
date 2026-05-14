/**
 * 权限指令
 * 功能：Vue指令用于根据权限动态显示/隐藏元素
 * 作者：System
 * 创建日期：2024-01-15
 */

import type { Directive, DirectiveBinding } from 'vue'
import { authStore } from '@/composables/system/usePermission'
import type { Permission } from '@/types/permission'

/**
 * v-permission 指令用法：
 * v-permission="'upload'" - 需要upload权限
 * v-permission="['upload', 'edit']" - 需要所有指定权限
 * v-permission="'admin'" - 需要管理员角色（super_admin）
 */

interface PermissionBinding {
  value?: Permission | Permission[] | { any?: Permission[]; all?: Permission[] } | string
  modifiers?: {
    disabled?: boolean
    show?: boolean
  }
}

/**
 * 检查是否有admin角色（仅 super_admin）
 */
function checkAdminRole(): boolean {
  const user = authStore.getUser()
  const userRole = user?.role as string | undefined
  return userRole === 'super_admin'
}

/**
 * 检查是否已登录（operator 或 super_admin）
 */
function checkLoggedInRole(): boolean {
  const user = authStore.getUser()
  const userRole = user?.role as string | undefined
  return userRole === 'super_admin' || userRole === 'operator'
}

/**
 * 检查是否有指定权限
 */
function checkPermission(binding: PermissionBinding): boolean {
  const { value } = binding

  if (!value) {
    return true
  }

  if (typeof value === 'string') {
    if (value === 'admin') {
      return checkAdminRole()
    }
    if (value === 'logged_in') {
      return checkLoggedInRole()
    }
    return authStore.hasPermission(value as Permission)
  }

  if (Array.isArray(value)) {
    return authStore.hasAllPermissions(value as Permission[])
  }

  if (typeof value === 'object') {
    if ('any' in value && value.any) {
      return authStore.hasAnyPermission(value.any)
    }
    if ('all' in value && value.all) {
      return authStore.hasAllPermissions(value.all)
    }
  }

  return true
}

function updateDirective(el: HTMLElement, binding: PermissionBinding, _vnode: unknown) {
  const hasPermission = checkPermission(binding)
  const showMode = binding.modifiers?.show || false

  if (showMode) {
    if (hasPermission) {
      el.style.display = ''
      el.removeAttribute('disabled')
    } else {
      el.style.display = 'none'
    }
    return
  }

  if (binding.modifiers?.disabled) {
    if (!hasPermission) {
      el.setAttribute('disabled', 'true')
      el.classList.add('opacity-50', 'cursor-not-allowed')
    } else {
      el.removeAttribute('disabled')
      el.classList.remove('opacity-50', 'cursor-not-allowed')
    }
    return
  }

  if (hasPermission) {
    el.style.display = ''
    el.removeAttribute('hidden')
  } else {
    el.setAttribute('hidden', 'true')
    el.style.display = 'none'
  }
}

export const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding, vnode) {
    updateDirective(el, binding as PermissionBinding, vnode)
  },
  updated(el: HTMLElement, binding: DirectiveBinding, vnode) {
    const oldValue = (binding as any).oldValue
    const newValue = (binding as any).value

    if (oldValue !== newValue) {
      updateDirective(el, binding as PermissionBinding, vnode)
    }
  }
}

export default permissionDirective
