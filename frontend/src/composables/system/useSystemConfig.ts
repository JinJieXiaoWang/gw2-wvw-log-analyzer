/**
 * useSystemConfig - 系统配置统一获取组合式函数
 * 功能：封装 sys_config 表的读写操作，提供响应式配置访问
 * 说明：系统配置影响系统运行方式，与字典表（纯映射）区分
 */

import { ref, computed } from 'vue'
import { settingsService } from '@/services'

interface SystemConfigItem {
  config_key: string
  config_name: string
  config_value: string
  config_type: string
}

const configCache = ref<Record<string, string>>({})
const configLoading = ref(false)
const configError = ref<Error | null>(null)
let isLoaded = false

/**
 * 加载系统配置（全局缓存，首次调用时触发）
 */
async function loadSystemConfigs(): Promise<void> {
  if (isLoaded) return
  configLoading.value = true
  configError.value = null
  try {
    const res = await settingsService.getSettings()
    if (res.success && res.data) {
      const data = res.data as Record<string, unknown>
      // 扁平化嵌套数据
      const flattened: Record<string, string> = {}
      for (const [key, value] of Object.entries(data)) {
        if (typeof value === 'object' && value !== null) {
          for (const [subKey, subValue] of Object.entries(value)) {
            flattened[`${key}.${subKey}`] = String(subValue)
          }
        } else {
          flattened[key] = String(value)
        }
      }
      configCache.value = flattened
      isLoaded = true
    }
  } catch (err) {
    configError.value = err instanceof Error ? err : new Error('加载系统配置失败')
    console.error('[useSystemConfig] 加载失败:', err)
  } finally {
    configLoading.value = false
  }
}

/**
 * 获取单个配置值（优先缓存）
 */
function getConfig(key: string, defaultValue: string = ''): string {
  return configCache.value[key] ?? defaultValue
}

/**
 * 获取布尔类型配置
 */
function getBoolConfig(key: string, defaultValue: boolean = false): boolean {
  const val = configCache.value[key]
  if (val === undefined) return defaultValue
  return val === 'true' || val === '1'
}

/**
 * 获取数值类型配置
 */
function getNumberConfig(key: string, defaultValue: number = 0): number {
  const val = configCache.value[key]
  if (val === undefined) return defaultValue
  const num = parseFloat(val)
  return isNaN(num) ? defaultValue : num
}

/**
 * 更新单个配置
 */
async function updateConfig(key: string, value: string | number | boolean): Promise<boolean> {
  try {
    const strValue = typeof value === 'boolean' ? value.toString() : String(value)
    const res = await settingsService.updateSystemSetting(key, strValue)
    if (res.success) {
      configCache.value[key] = strValue
      return true
    }
    return false
  } catch (err) {
    console.error(`[useSystemConfig] 更新 ${key} 失败:`, err)
    return false
  }
}

/**
 * 批量更新配置
 */
async function updateConfigs(updates: Record<string, string | number | boolean>): Promise<boolean> {
  try {
    const data: Record<string, string> = {}
    for (const [key, value] of Object.entries(updates)) {
      data[key] = typeof value === 'boolean' ? value.toString() : String(value)
    }
    const res = await settingsService.updateSettings(data)
    if (res.success) {
      Object.assign(configCache.value, data)
      return true
    }
    return false
  } catch (err) {
    console.error('[useSystemConfig] 批量更新失败:', err)
    return false
  }
}

/**
 * 刷新配置（强制重新加载）
 */
async function refreshConfigs(): Promise<void> {
  isLoaded = false
  await loadSystemConfigs()
}

export function useSystemConfig() {
  const loading = computed(() => configLoading.value)
  const error = computed(() => configError.value)
  const configs = computed(() => ({ ...configCache.value }))

  return {
    configs,
    loading,
    error,
    loadSystemConfigs,
    getConfig,
    getBoolConfig,
    getNumberConfig,
    updateConfig,
    updateConfigs,
    refreshConfigs,
  }
}
