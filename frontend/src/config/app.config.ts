/**
 * 应用配置中心（兼容导出层）
 *
 * ⚠️ 重要说明：
 * 本文件已从"独立配置源"重构为"统一配置管理器的兼容导出层"。
 * 所有配置项现在集中由 src/services/core/configManager.ts 管理。
 *
 * 推荐使用方式：
 *   import { configManager } from '@/services/core/configManager'
 *   const timeout = configManager.get('api').timeout
 *   const toastLife = configManager.get('ui').toastLife
 *
 * 兼容用法（仍然支持，但建议逐步迁移）：
 *   import { API_CONFIG } from '@/config/app.config'
 *   const timeout = API_CONFIG.timeout
 *
 * 配置优先级：环境变量 > 配置文件 > 默认值
 * 修改配置请优先编辑 .env 文件，无需修改代码。
 */

import { configManager } from '@/services/core/configManager'
import type {
  AppConfig,
  AppSettings,
  ApiSettings,
  CacheSettings,
  PaginationSettings,
  PollingSettings,
  DebounceSettings,
  UISettings,
  UploadSettings,
  ExportSettings,
  FeatureFlags,
  ThemeSettings,
  I18nSettings,
  SecuritySettings,
  PerformanceSettings
} from '@/services/core/configManager'

// 导出类型
export type {
  AppConfig,
  AppSettings,
  ApiSettings,
  CacheSettings,
  PaginationSettings,
  PollingSettings,
  DebounceSettings,
  UISettings,
  UploadSettings,
  ExportSettings,
  FeatureFlags,
  ThemeSettings,
  I18nSettings,
  SecuritySettings,
  PerformanceSettings
}

/**
 * API 配置（兼容导出）
 * @deprecated 请使用 configManager.get('api')
 * 保留大写属性别名以兼容旧代码（如 API_CONFIG.TIMEOUT）
 */
export const API_CONFIG = {
  ...configManager.get('api'),
  get TIMEOUT() { return configManager.get('api').timeout },
  get UPLOAD_TIMEOUT() { return configManager.get('api').uploadTimeout },
  get TOKEN_MONITOR_INTERVAL() { return configManager.get('api').tokenMonitorInterval },
  get NOTIFICATION_POLL_INTERVAL() { return configManager.get('api').notificationPollInterval },
}

/**
 * 缓存配置（兼容导出）
 * @deprecated 请使用 configManager.get('cache')
 */
export const CACHE_CONFIG = {
  ...configManager.get('cache'),
  get PROFESSION_TTL() { return configManager.get('cache').professionTtl },
  get DICT_MAPPING_TTL() { return configManager.get('cache').dictMappingTtl },
  get DEFAULT_API_TTL() { return configManager.get('cache').defaultApiTtl },
  get REQUEST_CACHE_TTL() { return configManager.get('cache').requestCacheTtl },
}

/**
 * 分页配置（兼容导出）
 * @deprecated 请使用 configManager.get('pagination')
 */
export const PAGINATION_CONFIG = configManager.get('pagination')

/**
 * 轮询配置（兼容导出）
 * @deprecated 请使用 configManager.get('polling')
 */
export const POLLING_CONFIG = configManager.get('polling')

/**
 * 防抖配置（兼容导出）
 * @deprecated 请使用 configManager.get('debounce')
 */
export const DEBOUNCE_CONFIG = configManager.get('debounce')

/**
 * UI 配置（兼容导出）
 * @deprecated 请使用 configManager.get('ui')
 */
export const UI_CONFIG = {
  ...configManager.get('ui'),
  get TOAST_LIFE() { return configManager.get('ui').toastLife },
  get TOAST_ERROR_LIFE() { return configManager.get('ui').toastErrorLife },
  get MOBILE_BREAKPOINT() { return configManager.get('ui').mobileBreakpoint },
  get TABLET_BREAKPOINT() { return configManager.get('ui').tabletBreakpoint },
  get DIALOG_MAX_WIDTH() { return configManager.get('ui').dialogMaxWidth },
  get MOBILE_DIALOG_WIDTH() { return configManager.get('ui').mobileDialogWidth },
}

/**
 * 上传配置（兼容导出）
 * @deprecated 请使用 configManager.get('upload')
 */
export const UPLOAD_CONFIG = configManager.get('upload')

/**
 * 导出配置（兼容导出）
 * @deprecated 请使用 configManager.get('export')
 */
export const EXPORT_CONFIG = configManager.get('export')

/** 完整配置对象（兼容导出）@deprecated 请使用 configManager.getConfig() */
export const APP_CONFIG = configManager.getConfig()

/** 统一配置管理器实例（推荐直接使用） */
export { configManager }

export default APP_CONFIG
