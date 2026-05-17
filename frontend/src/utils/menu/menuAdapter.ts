/**
 * 菜单数据适配器
 * 将项目标准菜单格式转换为 PrimeVue Menubar 格式
 */

import type { MenuItem as PrimeMenuItem } from 'primevue/menuitem'

/** 项目菜单项格式 */
export interface AppMenuItem {
  path?: string
  label: string
  icon?: string
  description?: string
  requireAuth?: boolean
  perms?: string
  children?: AppMenuItem[]
}

/**
 * 将项目菜单项转换为 PrimeVue Menubar 格式
 * @param items 项目格式菜单列表
 * @param onNavigate 导航回调函数
 */
export function adaptToMenubar(
  items: AppMenuItem[],
  onNavigate?: (path: string) => void
): PrimeMenuItem[] {
  return items
    .filter(item => item.path || item.children?.length)
    .map(item => {
      const primeItem: PrimeMenuItem = {
        label: item.label,
        icon: item.icon,
        ...(item.path
          ? {
              url: item.path,
              command: onNavigate ? () => onNavigate(item.path!) : undefined,
            }
          : {}),
      }

      if (item.children && item.children.length > 0) {
        primeItem.items = adaptToMenubar(item.children, onNavigate)
      }

      return primeItem
    })
}

/**
 * 展平树形菜单结构（用于需要扁平列表的场景，如移动端菜单）
 */
export function flattenMenus(menus: AppMenuItem[]): AppMenuItem[] {
  const result: AppMenuItem[] = []
  for (const menu of menus) {
    if (menu.path) {
      result.push(menu)
    }
    if (menu.children?.length) {
      result.push(...flattenMenus(menu.children))
    }
  }
  return result
}

/**
 * 根据权限过滤菜单项
 */
export function filterMenusByPermission(
  menus: AppMenuItem[],
  can: (perm: string) => boolean,
  isAuthenticated: boolean
): AppMenuItem[] {
  return menus.filter(item => {
    if (item.requireAuth && !isAuthenticated) return false
    if (item.perms && !can(item.perms)) return false
    if (item.children) {
      item.children = filterMenusByPermission(item.children, can, isAuthenticated)
    }
    return true
  })
}
