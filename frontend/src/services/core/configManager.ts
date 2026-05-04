/**
 * 配置管理系统
 * 功能：支持配置文件和环境变量的统一配置管理
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

export interface AppConfig {
  app: AppSettings
  api: ApiSettings
  features: FeatureFlags
  theme: ThemeSettings
  i18n: I18nSettings
  security: SecuritySettings
  performance: PerformanceSettings
}

export interface AppSettings {
  name: string
  version: string
  env: 'development' | 'production' | 'test'
  debug: boolean
  baseUrl: string
  uploadMaxSize: number
  supportedFormats: string[]
}

export interface ApiSettings {
  baseUrl: string
  timeout: number
  retryAttempts: number
  retryDelay: number
  mockEnabled: boolean
  mockDelay: number
}

export interface FeatureFlags {
  enableAI: boolean
  enableExport: boolean
  enableBuildParser: boolean
  enableSkillAnalysis: boolean
  enableAttendance: boolean
  enableDashboard: boolean
  enableRealtime: boolean
}

export interface ThemeSettings {
  mode: 'dark' | 'light' | 'auto'
  primaryColor: string
  secondaryColor: string
  accentColor: string
  fontSize: 'small' | 'medium' | 'large'
  compactMode: boolean
  animationEnabled: boolean
}

export interface I18nSettings {
  locale: string
  fallbackLocale: string
  dateFormat: string
  timeFormat: string
  numberFormat: string
}

export interface SecuritySettings {
  passwordMinLength: number
  passwordRequireUppercase: boolean
  passwordRequireLowercase: boolean
  passwordRequireNumbers: boolean
  passwordRequireSpecial: boolean
  sessionTimeout: number
  maxLoginAttempts: number
  lockoutDuration: number
}

export interface PerformanceSettings {
  enableCache: boolean
  cacheMaxAge: number
  lazyLoadEnabled: boolean
  virtualizationEnabled: boolean
  prefetchEnabled: boolean
  bundleAnalyzer: boolean
}

const DefaultConfig: AppConfig = {
  app: {
    name: 'GW2 WVW 日志解析系统',
    version: '2.0.0',
    env: 'development',
    debug: true,
    baseUrl: '/',
    uploadMaxSize: 100 * 1024 * 1024,
    supportedFormats: ['.zevtc', '.evtc']
  },

  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    mockEnabled: import.meta.env.VITE_MOCK_ENABLED === 'true',
    mockDelay: 500
  },

  features: {
    enableAI: true,
    enableExport: true,
    enableBuildParser: true,
    enableSkillAnalysis: true,
    enableAttendance: true,
    enableDashboard: true,
    enableRealtime: false
  },

  theme: {
    mode: 'dark',
    primaryColor: '#165DFF',
    secondaryColor: '#FF7D00',
    accentColor: '#00C896',
    fontSize: 'medium',
    compactMode: false,
    animationEnabled: true
  },

  i18n: {
    locale: 'zh-CN',
    fallbackLocale: 'en-US',
    dateFormat: 'YYYY-MM-DD',
    timeFormat: 'HH:mm:ss',
    numberFormat: 'zh-CN'
  },

  security: {
    passwordMinLength: 8,
    passwordRequireUppercase: true,
    passwordRequireLowercase: true,
    passwordRequireNumbers: true,
    passwordRequireSpecial: true,
    sessionTimeout: 3600,
    maxLoginAttempts: 5,
    lockoutDuration: 1800
  },

  performance: {
    enableCache: true,
    cacheMaxAge: 300000,
    lazyLoadEnabled: true,
    virtualizationEnabled: true,
    prefetchEnabled: true,
    bundleAnalyzer: false
  }
}

class ConfigManager {
  private config: AppConfig
  private listeners: Map<string, Set<(value: any, oldValue?: any) => void>> = new Map()
  private configFileCache: Map<string, any> = new Map()

  constructor() {
    this.config = this.loadConfig()
  }

  /**
   * 加载配置
   */
  private loadConfig(): AppConfig {
    const envConfig = this.loadFromEnv()
    return this.deepMerge(DefaultConfig, envConfig)
  }

  /**
   * 从环境变量加载配置
   */
  private loadFromEnv(): Partial<AppConfig> {
    const envConfig: Partial<AppConfig> = {}

    if (import.meta.env.VITE_APP_NAME) {
      envConfig.app = { ...DefaultConfig.app, name: import.meta.env.VITE_APP_NAME }
    }

    if (import.meta.env.VITE_API_BASE_URL) {
      envConfig.api = { ...DefaultConfig.api, baseUrl: import.meta.env.VITE_API_BASE_URL }
    }

    if (import.meta.env.VITE_DEBUG) {
      envConfig.app = { ...(envConfig.app || DefaultConfig.app), debug: import.meta.env.VITE_DEBUG === 'true' }
    }

    if (import.meta.env.VITE_MOCK_ENABLED) {
      envConfig.api = { ...(envConfig.api || DefaultConfig.api), mockEnabled: import.meta.env.VITE_MOCK_ENABLED === 'true' }
    }

    return envConfig
  }

  /**
   * 深度合并对象
   */
  private deepMerge<T extends Record<string, any>>(target: T, source: Partial<T>): T {
    const result = { ...target }

    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = { ...target[key], ...source[key] }
      } else if (source[key] !== undefined) {
        result[key] = source[key] as T[Extract<keyof T, string>]
      }
    }

    return result
  }

  /**
   * 获取完整配置
   */
  getConfig(): AppConfig {
    return { ...this.config }
  }

  /**
   * 获取指定模块配置
   */
  get<K extends keyof AppConfig>(key: K): AppConfig[K] {
    return this.config[key]
  }

  /**
   * 获取指定配置项
   */
  getValue<T = any>(path: string, defaultValue?: T): T {
    const keys = path.split('.')
    let result: any = this.config

    for (const key of keys) {
      if (result && typeof result === 'object' && key in result) {
        result = result[key]
      } else {
        return defaultValue as T
      }
    }

    return result ?? (defaultValue as T)
  }

  /**
   * 设置配置项
   */
  set(path: string, value: any): void {
    const keys = path.split('.')
    const lastKey = keys.pop()

    if (!lastKey) return

    let current: any = this.config
    for (const key of keys) {
      if (!(key in current)) {
        current[key] = {}
      }
      current = current[key]
    }

    const oldValue = current[lastKey]
    current[lastKey] = value

    this.notifyListeners(path, value, oldValue)
  }

  /**
   * 更新配置
   */
  update(updates: Partial<AppConfig>): void {
    this.config = this.deepMerge(this.config, updates)
    this.notifyAllListeners()
  }

  /**
   * 重置为默认配置
   */
  reset(): void {
    this.config = { ...DefaultConfig }
    this.notifyAllListeners()
  }

  /**
   * 加载配置文件
   */
  async loadConfigFile<T = any>(filePath: string, defaultValue?: T): Promise<T> {
    if (this.configFileCache.has(filePath)) {
      return this.configFileCache.get(filePath) as T
    }

    try {
      const response = await fetch(filePath)
      if (!response.ok) {
        throw new Error(`Failed to load config file: ${filePath}`)
      }
      const data = await response.json()
      this.configFileCache.set(filePath, data)
      return data as T
    } catch (error) {
      console.error(`[ConfigManager] Failed to load config file ${filePath}:`, error)
      return defaultValue as T
    }
  }

  /**
   * 检查功能开关
   */
  isFeatureEnabled(feature: keyof FeatureFlags): boolean {
    return this.config.features[feature]
  }

  /**
   * 切换功能开关
   */
  toggleFeature(feature: keyof FeatureFlags, enabled: boolean): void {
    const oldValue = this.config.features[feature]
    this.config.features[feature] = enabled
    this.notifyListeners(`features.${feature}`, enabled, oldValue)
  }

  /**
   * 获取主题配置
   */
  getTheme(): ThemeSettings {
    return { ...this.config.theme }
  }

  /**
   * 更新主题配置
   */
  setTheme(theme: Partial<ThemeSettings>): void {
    const oldTheme = { ...this.config.theme }
    this.config.theme = { ...this.config.theme, ...theme }
    this.notifyListeners('theme', this.config.theme, oldTheme)
  }

  /**
   * 订阅配置变更
   */
  subscribe(path: string, callback: (value: any, oldValue?: any) => void): () => void {
    if (!this.listeners.has(path)) {
      this.listeners.set(path, new Set())
    }
    this.listeners.get(path)!.add(callback)

    return () => {
      const pathListeners = this.listeners.get(path)
      if (pathListeners) {
        pathListeners.delete(callback)
      }
    }
  }

  /**
   * 通知监听器
   */
  private notifyListeners(path: string, newValue: any, oldValue: any): void {
    const listeners = this.listeners.get(path)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(newValue, oldValue)
        } catch (error) {
          console.error(`[ConfigManager] Config listener error for ${path}:`, error)
        }
      })
    }
  }

  /**
   * 通知所有监听器
   */
  private notifyAllListeners(): void {
    this.listeners.forEach((callbacks, path) => {
      const value = this.getValue(path)
      callbacks.forEach(callback => {
        try {
          callback(value)
        } catch (error) {
          console.error(`[ConfigManager] Config listener error for ${path}:`, error)
        }
      })
    })
  }

  /**
   * 导出配置为JSON
   */
  toJSON(): string {
    return JSON.stringify(this.config, null, 2)
  }

  /**
   * 从JSON导入配置
   */
  fromJSON(json: string): void {
    try {
      const parsed = JSON.parse(json)
      this.config = this.deepMerge(this.config, parsed)
      this.notifyAllListeners()
    } catch (error) {
      console.error('[ConfigManager] Failed to parse config JSON:', error)
      throw new Error('Invalid configuration JSON')
    }
  }
}

export const configManager = new ConfigManager()
export default configManager
