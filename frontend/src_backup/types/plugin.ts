/**
 * 插件系统核心接口
 * 功能：定义插件接口规范，支持功能模块的动态加载和卸载
 * 作者：System
 * 创建日期：2024-01-15
 */

/**
 * 插件元信息
 */
export interface PluginMeta {
  id: string
  name: string
  version: string
  description: string
  author: string
  dependencies?: string[]
  compatibility?: string
}

/**
 * 插件生命周期钩子
 */
export interface PluginHooks {
  onInstall?: () => Promise<void> | void
  onUninstall?: () => Promise<void> | void
  onEnable?: () => Promise<void> | void
  onDisable?: () => Promise<void> | void
  onUpdate?: (oldVersion: string) => Promise<void> | void
}

/**
 * 插件配置选项
 */
export interface PluginOptions {
  autoEnable?: boolean
  priority?: number
  config?: Record<string, any>
}

/**
 * 插件实例接口
 */
export interface Plugin {
  meta: PluginMeta
  hooks: PluginHooks
  options: PluginOptions
}

/**
 * 插件状态
 */
export type PluginStatus = 'installed' | 'enabled' | 'disabled' | 'error'

/**
 * 插件注册信息
 */
export interface PluginRegistration {
  plugin: Plugin
  status: PluginStatus
  error?: Error
  enabledAt?: Date
}

/**
 * 插件管理器配置
 */
export interface PluginManagerConfig {
  autoEnable: boolean
  pluginDir: string
  whitelist?: string[]
  blacklist?: string[]
}

/**
 * 插件API接口 - 插件可以调用宿主提供的功能
 */
export interface PluginAPI {
  registerRoute: (route: RouteConfig) => void
  registerComponent: (name: string, component: any) => void
  registerStore: (name: string, store: any) => void
  registerDirective: (name: string, directive: any) => void
  getConfig: <T = any>(key: string, defaultValue?: T) => T
  setConfig: (key: string, value: any) => void
  emit: (event: string, ...args: any[]) => void
  on: (event: string, callback: (...args: any[]) => void) => void
  off: (event: string, callback: (...args: any[]) => void) => void
}

/**
 * 路由配置
 */
export interface RouteConfig {
  path: string
  name?: string
  component?: any
  meta?: Record<string, any>
  children?: RouteConfig[]
}

/**
 * 插件上下文
 */
export interface PluginContext {
  api: PluginAPI
  config: Record<string, any>
}

/**
 * 插件包清单
 */
export interface PluginManifest {
  meta: PluginMeta
  main: string
  assets?: string[]
  styles?: string[]
}

/**
 * 创建插件的工厂函数类型
 */
export type PluginFactory = (context: PluginContext) => Plugin
