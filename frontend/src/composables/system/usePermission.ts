/**
 * 权限状态管理
 * 功能：集中管理用户认证状态和权限
 * 作者：System
 * 创建日期：2024-01-15
 * 更新：2026-05-11 - 优化字典预加载逻辑，不阻塞登录流程
 */

import { reactive, computed } from 'vue'
import type { User, Permission, Role, LoginCredentials, AuthState, MenuItem } from '@/types/permission'
import { GUEST_PERMISSIONS, OPERATOR_PERMISSIONS, SUPER_ADMIN_PERMISSIONS } from '@/types/permission'
import { apiFactory } from '@/services/core/apiService'
import { authService } from '@/services/auth/authService'
import { saveAccessToken, clearToken } from '@/utils/auth/tokenManager'

const STORAGE_KEY = 'gw2_wvw_auth'

class AuthStore {
  private state: AuthState
  private loginAttempts: Map<string, { attempts: number; lastAttemptTime: string; lockedUntil: string | null }>

  constructor() {
    this.state = reactive<AuthState>({
      isAuthenticated: false,
      user: null,
      permissions: GUEST_PERMISSIONS,
      token: null,
      menus: []
    })
    this.loginAttempts = new Map()
    this.loadFromStorage()
  }

  /**
   * 从localStorage加载认证状态
   */
  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored)
        if (data.isAuthenticated && data.user && data.token) {
          this.state.isAuthenticated = data.isAuthenticated
          this.state.user = data.user
          this.state.token = data.token
          this.state.permissions = this.getPermissionsByRole(data.user.role)
          
          // 同时保存token到统一 token 管理器
          saveAccessToken(data.token)
        }
      }
    } catch (error) {
      console.error('Failed to load auth state:', error)
      this.clearAuth()
    }
  }

  /**
   * 保存认证状态到localStorage
   */
  private saveToStorage(): void {
    try {
      const data = {
        isAuthenticated: this.state.isAuthenticated,
        user: this.state.user,
        token: this.state.token
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save auth state:', error)
    }
  }

  /**
   * 根据角色获取权限列表
   */
  private getPermissionsByRole(role: Role): Permission[] {
    switch (role) {
      case 'super_admin':
        return SUPER_ADMIN_PERMISSIONS
      case 'operator':
        return OPERATOR_PERMISSIONS
      default:
        return GUEST_PERMISSIONS
    }
  }

  /**
   * 根据权限字符串数组获取权限列表
   */
  private parsePermissions(permissions: string[]): Permission[] {
    const validPermissions: Permission[] = ['read', 'write', 'upload', 'delete', 'manage_users']
    return permissions.filter(p => validPermissions.includes(p as Permission)) as Permission[]
  }

  /**
   * 用户登录
   * 优化：字典预加载延迟到后台执行，不阻塞登录流程
   */
  public async login(credentials: LoginCredentials): Promise<{ success: boolean; message: string; error_code?: string }> {
    const { username, password } = credentials

    // 前端验证
    if (!username || username.length < 3 || username.length > 50) {
      return {
        success: false,
        message: '用户名长度需在3-50字符之间'
      }
    }
    if (!password || password.length < 6 || password.length > 128) {
      return {
        success: false,
        message: '密码长度需在6-128字符之间'
      }
    }

    // 检查账户锁定状态
    const attemptRecord = this.loginAttempts.get(username)
    const now = new Date()
    if (attemptRecord?.lockedUntil && new Date(attemptRecord.lockedUntil) > now) {
      const remainingMinutes = Math.ceil((new Date(attemptRecord.lockedUntil).getTime() - now.getTime()) / 60000)
      return {
        success: false,
        message: `账户已锁定，请${remainingMinutes}分钟后再试`
      }
    }

    try {
      const result = await apiFactory.post<any>('/api/v1/auth/login', { username, password }) as {
        success: boolean
        message?: string
        error_code?: string
        data?: {
          access_token: string
          user: Record<string, unknown>
          permissions: string[]
          menus: MenuItem[]
        }
      }

      if (result.success && result.data) {
        const { access_token, user, permissions, menus } = result.data
        
        // 重置登录尝试记录
        this.loginAttempts.delete(username)

        // 更新状态
        this.state.isAuthenticated = true
        this.state.user = {
          id: String((user as Record<string, unknown>).id),
          username: (user as Record<string, unknown>).username as string,
          role: ((user as Record<string, unknown>).role as Role) || 'operator',
          loginTime: new Date().toISOString(),
          lastActiveTime: new Date().toISOString()
        }
        this.state.permissions = permissions.length > 0 
          ? this.parsePermissions(permissions) 
          : this.getPermissionsByRole((user.role as Role) || 'operator')
        this.state.token = access_token
        this.state.menus = menus || []
        
        // 保存token到统一 token 管理器，确保API请求能正确携带token
        saveAccessToken(access_token)
        
        this.saveToStorage()

        // 优化：延迟到后台预加载字典，完全不阻塞登录流程
        // 使用 setTimeout 确保在下一个事件循环中执行
        setTimeout(() => {
          import('@/store/system/dict')
            .then(({ useDictStore }) => {
              const dictStore = useDictStore()
              return dictStore.preloadCommonDicts()
            })
            .catch((e) => {
              console.warn('[AuthStore] 预加载字典失败:', e)
            })
        }, 100)

        return {
          success: true,
          message: result.message || '登录成功'
        }
      } else {
        // 记录登录失败尝试
        const attempts = attemptRecord?.attempts || 0
        const newAttempts = attempts + 1
        
        if (newAttempts >= 5) {
          const lockedUntil = new Date(now.getTime() + 15 * 60 * 1000).toISOString()
          this.loginAttempts.set(username, {
            attempts: newAttempts,
            lastAttemptTime: now.toISOString(),
            lockedUntil
          })
          return {
            success: false,
            message: '登录失败次数过多，账户已锁定15分钟',
            error_code: result.error_code
          }
        } else {
          this.loginAttempts.set(username, {
            attempts: newAttempts,
            lastAttemptTime: now.toISOString(),
            lockedUntil: null
          })
          return {
            success: false,
            message: result.message || '登录失败',
            error_code: result.error_code
          }
        }
      }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        message: '网络异常，请稍后重试'
      }
    }
  }

  /**
   * 用户登出
   */
  public async logout(): Promise<void> {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      this.clearAuth()
    }
  }

  /**
   * 获取登录状态
   */
  public async getStatus(): Promise<{ is_logged_in: boolean; user: User | null; permissions: Permission[]; menus: MenuItem[] }> {
    try {
      const result = await apiFactory.get<any>('/api/v1/auth/status')

      if (result.success && result.data) {
        const { is_logged_in, user, permissions, menus } = result.data
        
        if (is_logged_in && user) {
          this.state.isAuthenticated = true
          this.state.user = {
            id: user.id.toString(),
            username: user.username,
            role: (user.role as Role) || 'operator',
            loginTime: user.last_login,
            lastActiveTime: new Date().toISOString()
          }
          this.state.permissions = permissions.length > 0 
            ? this.parsePermissions(permissions) 
            : this.getPermissionsByRole((user.role as Role) || 'operator')
          this.state.menus = menus || []
          
          this.saveToStorage()
          
          return {
            is_logged_in: true,
            user: this.state.user,
            permissions: this.state.permissions,
            menus: this.state.menus
          }
        }
      }
      
      // 如果未登录，获取公开菜单
      await this.loadPublicMenus()
      
      return {
        is_logged_in: false,
        user: null,
        permissions: GUEST_PERMISSIONS,
        menus: this.state.menus
      }
    } catch (error) {
      console.error('Get status error:', error)
      
      // 出错时也尝试获取公开菜单
      try {
        await this.loadPublicMenus()
      } catch (e) {
        console.error('Load public menus error:', e)
      }
      
      return {
        is_logged_in: false,
        user: null,
        permissions: GUEST_PERMISSIONS,
        menus: this.state.menus
      }
    }
  }

  /**
   * 加载公开菜单
   */
  public async loadPublicMenus(): Promise<void> {
    try {
      const result = await apiFactory.get<any>('/api/v1/menus/public')
      if (result.success && result.data) {
        this.state.menus = result.data
        this.saveToStorage()
      }
    } catch (error) {
      console.error('Failed to load public menus:', error)
      // 如果无法获取公开菜单，使用默认菜单
      this.state.menus = this.getDefaultMenus()
    }
  }

  /**
   * 获取默认菜单
   */
  private getDefaultMenus(): MenuItem[] {
    return [
      {
        menu_name: '数据看板',
        path: '/',
        icon: 'pi pi-chart-line',
        menu_type: 'C'
      },
      {
        menu_name: '日志管理',
        path: '',
        icon: 'pi pi-file',
        menu_type: 'M',
        children: [
          {
            menu_name: '日志列表',
            path: '/logs',
            icon: 'pi pi-file',
            menu_type: 'C'
          }
        ]
      },
      {
        menu_name: '出勤统计',
        path: '/attendance',
        icon: 'pi pi-users',
        menu_type: 'C'
      },
      {
        menu_name: '技能循环',
        path: '/skill-analysis',
        icon: 'pi pi-sync',
        menu_type: 'C'
      },
      {
        menu_name: 'Build管理',
        path: '',
        icon: 'pi pi-code',
        menu_type: 'M',
        children: [
          {
            menu_name: '配置图书馆',
            path: '/builds',
            icon: 'pi pi-book',
            menu_type: 'C'
          },
          {
            menu_name: 'Build解析',
            path: '/build-parser',
            icon: 'pi pi-code',
            menu_type: 'C'
          }
        ]
      }
    ]
  }

  /**
   * 清除认证状态
   */
  public clearAuth(): void {
    this.state.isAuthenticated = false
    this.state.user = null
    this.state.permissions = GUEST_PERMISSIONS
    this.state.token = null
    // 清除菜单时保留公开菜单
    this.loadPublicMenus()
    localStorage.removeItem(STORAGE_KEY)
    clearToken()
  }

  /**
   * 获取用户菜单
   */
  public get menus(): MenuItem[] {
    return this.state.menus
  }

  /**
   * 检查是否有指定权限
   */
  public hasPermission(permission: Permission): boolean {
    return this.state.permissions.includes(permission)
  }

  /**
   * 检查是否有任一权限
   */
  public hasAnyPermission(permissions: Permission[]): boolean {
    return permissions.some(p => this.state.permissions.includes(p))
  }

  /**
   * 检查是否有所有权限
   */
  public hasAllPermissions(permissions: Permission[]): boolean {
    return permissions.every(p => this.state.permissions.includes(p))
  }

  // Getters
  get isAuthenticated() {
    return this.state.isAuthenticated
  }

  get user() {
    return this.state.user
  }

  get permissions() {
    return this.state.permissions
  }

  get token() {
    return this.state.token
  }

  get currentRole(): Role | null {
    return this.state.user?.role || null
  }

  get currentUser(): User | null {
    return this.state.user
  }

  getUser(): User | null {
    return this.state.user
  }

  validatePassword(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    if (password.length < 8) errors.push('密码长度至少8位')
    if (!/[A-Z]/.test(password)) errors.push('需包含大写字母')
    if (!/[a-z]/.test(password)) errors.push('需包含小写字母')
    if (!/[0-9]/.test(password)) errors.push('需包含数字')
    if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)) errors.push('需包含特殊字符')
    return { valid: errors.length === 0, errors }
  }

  setAdminConfig(username: string, password: string): { success: boolean; message: string } {
    try {
      localStorage.setItem('gw2_admin_config', JSON.stringify({ username, password }))
      return { success: true, message: '保存成功' }
    } catch {
      return { success: false, message: '保存失败' }
    }
  }

  getAdminConfig(): { username: string; password: string } {
    try {
      const stored = localStorage.getItem('gw2_admin_config')
      if (stored) {
        const parsed = JSON.parse(stored)
        return { username: parsed.username || '', password: parsed.password || '' }
      }
    } catch {
      // ignore
    }
    return { username: this.state.user?.username || '', password: '' }
  }
}

// 导出单例
export const authStore = new AuthStore()

// 导出 composable
export function usePermission() {
  return {
    isAuthenticated: computed(() => authStore.isAuthenticated),
    user: computed(() => authStore.user),
    permissions: computed(() => authStore.permissions),
    token: computed(() => authStore.token),
    menus: computed(() => authStore.menus),
    isAdmin: computed(() => authStore.user?.role === 'super_admin'),
    isOperator: computed(() => authStore.user?.role === 'operator'),
    isSuperAdmin: computed(() => authStore.user?.role === 'super_admin'),
    login: authStore.login.bind(authStore),
    logout: authStore.logout.bind(authStore),
    getStatus: authStore.getStatus.bind(authStore),
    loadPublicMenus: authStore.loadPublicMenus.bind(authStore),
    clearAuth: authStore.clearAuth.bind(authStore),
    hasPermission: authStore.hasPermission.bind(authStore),
    hasAnyPermission: authStore.hasAnyPermission.bind(authStore),
    hasAllPermissions: authStore.hasAllPermissions.bind(authStore),
    can: (permission: Permission) => authStore.hasPermission(permission)
  }
}
