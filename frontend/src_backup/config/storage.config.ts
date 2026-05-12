/**
 * 本地存储键名统一管理
 *
 * 规范说明：
 * - 所有 localStorage / sessionStorage 键名必须从此文件导入
 * - 禁止在业务代码中直接硬编码 storage key
 * - 统一使用 `gw2_wvw_` 前缀（历史遗留的 `gw2_admin_` 键名保留兼容读取）
 *
 * 使用示例：
 *   import { STORAGE_KEYS } from '@/config/storage.config'
 *   localStorage.setItem(STORAGE_KEYS.TOKEN, token)
 */

/** ͳһǰ׺ */
export const STORAGE_PREFIX = 'gw2_wvw_'

/** Token 相关 */
export const TOKEN_KEYS = {
  /** 访问令牌（新键名，与 tokenManager.ts 一致） */
  ACCESS_TOKEN: 'gw2_admin_access_token',
  /** Token 过期时间戳（新键名，与 tokenManager.ts 一致） */
  TOKEN_EXPIRY: 'gw2_admin_token_expiry',
  /** 旧系统 Token（兼容） */
  LEGACY_TOKEN: 'gw2_wvw_token',
  /** 刷新令牌 */
  REFRESH_TOKEN: 'gw2_wvw_refresh_token',
} as const

/** 认证与权限 */
export const AUTH_KEYS = {
  /** 认证状态 */
  AUTH_STATE: 'gw2_wvw_auth',
  /** 管理员配置 */
  ADMIN_CONFIG: 'gw2_wvw_admin_config',
  /** 登录后重定向路径 */
  REDIRECT_PATH: 'auth_redirect',
} as const

/** 用户设置 */
export const SETTINGS_KEYS = {
  /** 应用设置 */
  APP_SETTINGS: 'gw2_wvw_settings',
  /** 当前主题 ID */
  THEME_ID: 'gw2_wvw_theme_id',
} as const

/** 其他功能 */
export const FEATURE_KEYS = {
  /** Token 已校验标记（路由守卫用） */
  TOKEN_VALIDATED: 'auth_token_validated',
} as const

/** 完整 Storage Keys 对象（兼容旧代码直接引用） */
export const STORAGE_KEYS = {
  ...TOKEN_KEYS,
  ...AUTH_KEYS,
  ...SETTINGS_KEYS,
  ...FEATURE_KEYS,
} as const

/** 获取带前缀的键名（用于新功能） */
export function getStorageKey(name: string): string {
  return `${STORAGE_PREFIX}${name}`
}

export default STORAGE_KEYS
