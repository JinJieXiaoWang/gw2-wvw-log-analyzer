/**
 * 插件管理器服务
 * 功能：管理插件的安装、启用、禁用、卸载生命周期
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import type {
  Plugin,
  PluginMeta,
  PluginRegistration,
  PluginStatus,
  PluginManagerConfig,
  PluginAPI,
  PluginContext,
  RouteConfig
} from '@/types/plugin'

class PluginManager {
  private plugins: Map<string, PluginRegistration> = new Map()
  private eventListeners: Map<string, Set<(...args: any[]) => void>> = new Map()
  private configStore: Map<string, any> = new Map()
  private registeredRoutes: RouteConfig[] = []
  private registeredComponents: Map<string, any> = new Map()
  private registeredStores: Map<string, any> = new Map()
  private registeredDirectives: Map<string, any> = new Map()

  private readonly defaultConfig: PluginManagerConfig = {
    autoEnable: true,
    pluginDir: '/plugins',
    whitelist: [],
    blacklist: []
  }

  private config: PluginManagerConfig

  constructor(config: Partial<PluginManagerConfig> = {}) {
    this.config = { ...this.defaultConfig, ...config }
  }

  /**
   * 获取插件API
   */
  private createPluginAPI(): PluginAPI {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const manager = this
    return {
      registerRoute: (route: RouteConfig) => {
        manager.registeredRoutes.push(route)
        manager.emitEvent('route:registered', route)
      },

      registerComponent: (name: string, component: any) => {
        manager.registeredComponents.set(name, component)
        manager.emitEvent('component:registered', name)
      },

      registerStore: (name: string, store: any) => {
        manager.registeredStores.set(name, store)
        manager.emitEvent('store:registered', name)
      },

      registerDirective: (name: string, directive: any) => {
        manager.registeredDirectives.set(name, directive)
        manager.emitEvent('directive:registered', name)
      },

      getConfig: <T = any>(key: string, defaultValue?: T): T => {
        return manager.configStore.get(key) ?? defaultValue as T
      },

      setConfig: (key: string, value: any) => {
        manager.configStore.set(key, value)
        manager.emitEvent('config:changed', { key, value })
      },

      emit: (event: string, ...args: any[]) => {
        manager.emitEvent(event, ...args)
      },

      on: (event: string, callback: (...args: any[]) => void) => {
        manager.addEventListener(event, callback)
      },

      off: (event: string, callback: (...args: any[]) => void) => {
        manager.removeEventListener(event, callback)
      }
    }
  }

  /**
   * 创建插件上下文
   */
  private createPluginContext(config?: Record<string, any>): PluginContext {
    return {
      api: this.createPluginAPI(),
      config: config || {}
    }
  }

  /**
   * 安装插件
   */
  async install(plugin: Plugin): Promise<void> {
    const { id } = plugin.meta

    if (this.plugins.has(id)) {
      console.warn(`[PluginManager] Plugin ${id} is already installed`)
      return
    }

    const registration: PluginRegistration = {
      plugin,
      status: 'installed'
    }

    this.plugins.set(id, registration)
    this.emitEvent('plugin:installed', plugin.meta)

    console.log(`[PluginManager] Plugin ${id} v${plugin.meta.version} installed`)

    if (this.config.autoEnable && plugin.options.autoEnable !== false) {
      await this.enable(id)
    }
  }

  /**
   * 卸载插件
   */
  async uninstall(pluginId: string): Promise<void> {
    const registration = this.plugins.get(pluginId)

    if (!registration) {
      console.warn(`[PluginManager] Plugin ${pluginId} is not installed`)
      return
    }

    if (registration.status === 'enabled') {
      await this.disable(pluginId)
    }

    if (registration.plugin.hooks.onUninstall) {
      try {
        await registration.plugin.hooks.onUninstall()
      } catch (error) {
        console.error(`[PluginManager] Plugin ${pluginId} uninstall hook failed:`, error)
      }
    }

    this.plugins.delete(pluginId)
    this.emitEvent('plugin:uninstalled', pluginId)

    console.log(`[PluginManager] Plugin ${pluginId} uninstalled`)
  }

  /**
   * 启用插件
   */
  async enable(pluginId: string): Promise<void> {
    const registration = this.plugins.get(pluginId)

    if (!registration) {
      throw new Error(`[PluginManager] Plugin ${pluginId} is not installed`)
    }

    if (registration.status === 'enabled') {
      console.warn(`[PluginManager] Plugin ${pluginId} is already enabled`)
      return
    }

    if (registration.status === 'error') {
      console.warn(`[PluginManager] Plugin ${pluginId} is in error state, cannot enable`)
      return
    }

    try {
      this.createPluginContext(registration.plugin.options.config)

      if (registration.plugin.hooks.onEnable) {
        await registration.plugin.hooks.onEnable()
      }

      registration.status = 'enabled'
      registration.enabledAt = new Date()
      this.emitEvent('plugin:enabled', pluginId)

      console.log(`[PluginManager] Plugin ${pluginId} enabled`)
    } catch (error) {
      registration.status = 'error'
      registration.error = error as Error
      console.error(`[PluginManager] Failed to enable plugin ${pluginId}:`, error)
      throw error
    }
  }

  /**
   * 禁用插件
   */
  async disable(pluginId: string): Promise<void> {
    const registration = this.plugins.get(pluginId)

    if (!registration) {
      throw new Error(`[PluginManager] Plugin ${pluginId} is not installed`)
    }

    if (registration.status !== 'enabled') {
      console.warn(`[PluginManager] Plugin ${pluginId} is not enabled`)
      return
    }

    try {
      if (registration.plugin.hooks.onDisable) {
        await registration.plugin.hooks.onDisable()
      }

      registration.status = 'disabled'
      this.emitEvent('plugin:disabled', pluginId)

      console.log(`[PluginManager] Plugin ${pluginId} disabled`)
    } catch (error) {
      console.error(`[PluginManager] Failed to disable plugin ${pluginId}:`, error)
      throw error
    }
  }

  /**
   * 获取插件状态
   */
  getPluginStatus(pluginId: string): PluginStatus | undefined {
    return this.plugins.get(pluginId)?.status
  }

  /**
   * 获取所有插件
   */
  getAllPlugins(): PluginMeta[] {
    return Array.from(this.plugins.values()).map(reg => reg.plugin.meta)
  }

  /**
   * 获取已启用的插件
   */
  getEnabledPlugins(): PluginMeta[] {
    return Array.from(this.plugins.values())
      .filter(reg => reg.status === 'enabled')
      .map(reg => reg.plugin.meta)
  }

  /**
   * 获取已注册的路由
   */
  getRegisteredRoutes(): RouteConfig[] {
    return [...this.registeredRoutes]
  }

  /**
   * 获取已注册组件
   */
  getRegisteredComponents(): Map<string, any> {
    return new Map(this.registeredComponents)
  }

  /**
   * 事件监听
   */
  addEventListener(event: string, callback: (...args: any[]) => void): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)
  }

  /**
   * 取消事件监听
   */
  removeEventListener(event: string, callback: (...args: any[]) => void): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  /**
   * 触发事件
   */
  private emitEvent(event: string, ...args: any[]): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(...args)
        } catch (error) {
          console.error(`[PluginManager] Event handler error for ${event}:`, error)
        }
      })
    }
  }

  /**
   * 设置配置项
   */
  setConfig(key: string, value: any): void {
    this.configStore.set(key, value)
    this.emitEvent('config:changed', { key, value })
  }

  /**
   * 获取配置项
   */
  getConfig<T = any>(key: string, defaultValue?: T): T {
    return this.configStore.get(key) ?? defaultValue as T
  }

  /**
   * 更新管理器配置
   */
  updateConfig(config: Partial<PluginManagerConfig>): void {
    this.config = { ...this.config, ...config }
  }
}

export const pluginManager = new PluginManager()
export default pluginManager
