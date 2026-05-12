/**
 * 设置状态管理
 * 功能：管理应用配置、主题等设置
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { ThemeService } from '@/services/system/themeService'
import { DEFAULT_THEME_ID } from '@/config/themes'
import { settingsService } from '@/services'

export type ThemeMode = 'light' | 'dark' | 'system'

export interface AppSettings {
  theme: ThemeMode
  gameThemeId: string
  language: string
  autoSave: boolean
  notifications: boolean
  defaultMap: string
  defaultServer: string
  watermarkEnabled: boolean
  watermarkText: string
  watermarkScreenshotEnabled: boolean
}

const STORAGE_KEY = 'gw2_wvw_settings'

const defaultSettings: AppSettings = {
  theme: 'dark',
  gameThemeId: DEFAULT_THEME_ID,
  language: 'zh-CN',
  autoSave: true,
  notifications: true,
  defaultMap: '',
  defaultServer: '',
  watermarkEnabled: false,
  watermarkText: '',
  watermarkScreenshotEnabled: true
}

function loadSettings(): AppSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      console.info(`[SettingsStore] Loaded settings from localStorage:`, parsed)
      return { 
        ...defaultSettings, 
        ...parsed,
        gameThemeId: parsed.gameThemeId || DEFAULT_THEME_ID
      }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
  return defaultSettings
}

function saveSettings(settings: AppSettings) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch (error) {
    console.error('Failed to save settings:', error)
  }
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>(loadSettings())

  // 监听变化自动保存
  watch(settings, (newSettings) => {
    saveSettings(newSettings)
    applyThemeMode(newSettings.theme)
    // 确保主题ID同步到ThemeService
    if (newSettings.gameThemeId) {
      ThemeService.applyTheme(newSettings.gameThemeId, false)
    }
  }, { deep: true })

  // 应用明暗模式
  function applyThemeMode(theme: ThemeMode) {
    const root = document.documentElement
    
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.toggle('dark', prefersDark)
    } else {
      root.classList.toggle('dark', theme === 'dark')
    }
  }

  // 切换游戏主题
  function setGameTheme(themeId: string) {
    if (ThemeService.themeExists(themeId)) {
      console.info(`[SettingsStore] Setting game theme: ${themeId}`)
      settings.value.gameThemeId = themeId
      ThemeService.applyTheme(themeId, false)
    }
  }

  // 获取当前游戏主题
  function getCurrentGameTheme() {
    return ThemeService.getCurrentTheme()
  }

  // 更新单个设置
  function updateSetting<K extends keyof AppSettings>(key: K, value: AppSettings[K]) {
    settings.value[key] = value
  }

  // 批量更新设置
  function updateSettings(partialSettings: Partial<AppSettings>) {
    Object.assign(settings.value, partialSettings)
    if (partialSettings.gameThemeId) {
      ThemeService.applyTheme(partialSettings.gameThemeId)
    }
  }

  // 重置为默认设置
  function resetSettings() {
    settings.value = { ...defaultSettings }
    ThemeService.resetToDefault()
  }

  // 从后端同步全局设置（优先使用服务器配置，特别是水印等全局策略）
  async function syncFromServer() {
    try {
      const result = await settingsService.getSettings()
      if (result.success && result.data) {
        const server = result.data
        // 水印配置：服务器全局优先
        if (typeof server.watermark_enabled === 'boolean') {
          settings.value.watermarkEnabled = server.watermark_enabled
        }
        if (typeof server.watermark_text === 'string') {
          settings.value.watermarkText = server.watermark_text
        }
        if (typeof server.watermark_screenshot_enabled === 'boolean') {
          settings.value.watermarkScreenshotEnabled = server.watermark_screenshot_enabled
        }
        // 其他配置也同步
        if (server.theme) settings.value.theme = server.theme
        if (server.default_server) settings.value.defaultServer = server.default_server
        console.info('[SettingsStore] Synced from server:', server)
      }
    } catch (e) {
      console.warn('[SettingsStore] Failed to sync from server:', e)
    }
  }

  // 初始化主题
  applyThemeMode(settings.value.theme)

  return {
    settings,
    applyThemeMode,
    setGameTheme,
    getCurrentGameTheme,
    updateSetting,
    updateSettings,
    resetSettings,
    syncFromServer
  }
})