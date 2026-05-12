/**
 * 权限类型定义
 * 功能：定义权限系统的核心类型
 * 作者：System
 * 创建日期：2024-01-15
 */

export type Permission = 'read' | 'write' | 'upload' | 'delete' | 'manage_users'

export type Role = 'guest' | 'operator' | 'super_admin'

export interface User {
  id: string
  username: string
  role: Role
  loginTime?: string
  lastActiveTime?: string
}

export interface LoginCredentials {
  username: string
  password: string
  rememberMe?: boolean
}

export interface MenuItem {
  menu_name: string
  path: string
  icon: string
  menu_type: 'M' | 'C'
  children?: MenuItem[]
}

export interface AuthState {
  isAuthenticated: boolean
  user: User | null
  permissions: Permission[]
  token: string | null
  menus: MenuItem[]
}

export interface LoginAttempt {
  username: string
  attempts: number
  lastAttemptTime: string
  lockedUntil: string | null
}

export const PERMISSION_DESCRIPTIONS: Record<Permission, string> = {
  read: '读取数据',
  write: '写入数据',
  upload: '上传文件',
  delete: '删除数据',
  manage_users: '管理用户'
}

export const GUEST_PERMISSIONS: Permission[] = ['read']

export const OPERATOR_PERMISSIONS: Permission[] = [
  'read', 'write', 'upload', 'delete'
]

export const SUPER_ADMIN_PERMISSIONS: Permission[] = [
  'read', 'write', 'upload', 'delete', 'manage_users'
]