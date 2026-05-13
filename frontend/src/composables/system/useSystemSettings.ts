import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { settingsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { useSettingsStore } from '@/store/system/settings'
import { authStore } from '@/composables/system/usePermission'
import {
  SETTING_SECTIONS,
  EXPORT_FORMAT_OPTIONS,
  THEME_COLOR_OPTIONS,
  NUMBER_FORMAT_OPTIONS,
  ACCOUNT_SETTINGS_DEFAULTS,
  PARSING_SETTINGS_DEFAULTS,
  EXPORT_SETTINGS_DEFAULTS,
  THEME_SETTINGS_DEFAULTS,
  NOTIFICATION_SETTINGS_DEFAULTS,
  SECURITY_SETTINGS_DEFAULTS
} from '@/constants/settings'
import { useDictOptions } from './useDictOptions'

export function useSystemSettings() {
  const toast = useToast()
  const router = useRouter()
  const settingsStore = useSettingsStore()

  const isLoadingSettings = ref(false)
  const isSavingSettings = ref(false)
  const isLoggingOut = ref(false)

  const activeSection = ref('account')

  const settingSections = SETTING_SECTIONS

  const accountSettings = reactive({ ...ACCOUNT_SETTINGS_DEFAULTS })

  const parsingSettings = reactive({ ...PARSING_SETTINGS_DEFAULTS })

  const exportSettings = reactive({ ...EXPORT_SETTINGS_DEFAULTS })

  const themeSettings = reactive({ ...THEME_SETTINGS_DEFAULTS })

  const notificationSettings = reactive({ ...NOTIFICATION_SETTINGS_DEFAULTS })

  const securitySettings = reactive({ ...SECURITY_SETTINGS_DEFAULTS })

  const watermarkSettings = reactive({
    watermarkEnabled: settingsStore.settings.watermarkEnabled,
    watermarkText: settingsStore.settings.watermarkText,
    watermarkScreenshotEnabled: settingsStore.settings.watermarkScreenshotEnabled
  })

  const lastLoginTime = ref('')

  const exportFormats = EXPORT_FORMAT_OPTIONS

  const themeColors = THEME_COLOR_OPTIONS

  const { options: numberFormatOptions } = useDictOptions('number_format', true, NUMBER_FORMAT_OPTIONS as any)

  const fetchSettings = async () => {
    isLoadingSettings.value = true
    try {
      const result = await ApiResponseWrapper.wrap(
        settingsService.getSettings(),
        { showErrorMessage: false }
      )
      if (result.success && result.data) {
        const data = result.data as any
        themeSettings.mode = data.theme === 'light' ? 'light' : 'dark'
        exportSettings.defaultFormat = data.export_format || 'csv'
        parsingSettings.preFightBuffer = data.parse_parallel || 5
        if (data.last_login_time) {
          lastLoginTime.value = data.last_login_time
        }
        if (data.username) {
          accountSettings.username = data.username
        }
        if (data.email) {
          accountSettings.email = data.email
        }
      }
    } finally {
      isLoadingSettings.value = false
    }
  }

  const saveSettings = async () => {
    isSavingSettings.value = true
    try {
      const settingsData = {
        theme: themeSettings.mode,
        export_format: exportSettings.defaultFormat,
        parse_parallel: parsingSettings.preFightBuffer
      }
      await ApiResponseWrapper.wrap(
        settingsService.updateSettings(settingsData),
        { showSuccessMessage: true, successMessage: '设置已保存', showErrorMessage: true }
      )
    } finally {
      isSavingSettings.value = false
    }
  }

  const saveAccountSettings = async () => {
    try {
      await ApiResponseWrapper.wrap(
        settingsService.updateSettings({
          username: accountSettings.username,
          email: accountSettings.email,
          bio: accountSettings.bio
        }),
        { showSuccessMessage: true, successMessage: '账号设置已保存', showErrorMessage: true }
      )
    } catch {
      // 错误已由 ApiResponseWrapper 处理
    }
  }

  const saveParsingSettings = async () => {
    try {
      await ApiResponseWrapper.wrap(
        settingsService.updateSettings({
          parsing_include_overkill: parsingSettings.includeOverkill,
          parsing_ignore_small_damage: parsingSettings.ignoreSmallDamage,
          parsing_pre_fight_buffer: parsingSettings.preFightBuffer,
          parsing_auto_categorize_skills: parsingSettings.autoCategorizeSkills
        }),
        { showSuccessMessage: true, successMessage: '解析参数已保存', showErrorMessage: true }
      )
    } catch {
      // 错误已由 ApiResponseWrapper 处理
    }
  }

  const saveExportSettings = async () => {
    try {
      await ApiResponseWrapper.wrap(
        settingsService.updateSettings({
          export_format: exportSettings.defaultFormat,
          export_include_header: exportSettings.includeHeader,
          export_utf8_encoding: exportSettings.utf8Encoding,
          export_number_format: exportSettings.numberFormat
        }),
        { showSuccessMessage: true, successMessage: '导出格式已保存', showErrorMessage: true }
      )
    } catch {
      // 错误已由 ApiResponseWrapper 处理
    }
  }

  const applyTheme = async () => {
    try {
      await ApiResponseWrapper.wrap(
        settingsService.updateSettings({
          theme: themeSettings.mode,
          theme_primary_color: themeSettings.primaryColor,
          theme_zoom: themeSettings.zoom
        }),
        { showSuccessMessage: true, successMessage: '主题已应用', showErrorMessage: true }
      )
    } catch {
      // 错误已由 ApiResponseWrapper 处理
    }
  }

  const saveNotificationSettings = async () => {
    try {
      await ApiResponseWrapper.wrap(
        settingsService.updateSettings({
          notification_email: notificationSettings.email,
          notification_push: notificationSettings.push,
          notification_parse_complete: notificationSettings.parseComplete
        }),
        { showSuccessMessage: true, successMessage: '通知设置已保存', showErrorMessage: true }
      )
    } catch {
      // 错误已由 ApiResponseWrapper 处理
    }
  }

  const saveWatermarkSettings = async (settings: { watermarkEnabled: boolean; watermarkText: string; watermarkScreenshotEnabled: boolean }) => {
    Object.assign(watermarkSettings, settings)
    settingsStore.updateSettings({
      watermarkEnabled: settings.watermarkEnabled,
      watermarkText: settings.watermarkText,
      watermarkScreenshotEnabled: settings.watermarkScreenshotEnabled
    })
    try {
      const result = await settingsService.updateSettings({
        watermark_enabled: settings.watermarkEnabled,
        watermark_text: settings.watermarkText,
        watermark_screenshot_enabled: settings.watermarkScreenshotEnabled
      })
      if (!result.success) {
        toast.add({ severity: 'error', summary: '同步失败', detail: result.message || '服务器保存失败', life: 5000 })
        return
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '同步失败', detail: e?.message || '服务器保存失败', life: 5000 })
      return
    }
    toast.add({ severity: 'success', summary: '保存成功', detail: '水印设置已保存并同步到服务器', life: 3000 })
  }

  const logout = async () => {
    isLoggingOut.value = true
    try {
      await authStore.logout()
      toast.add({ severity: 'success', summary: '登出成功', detail: '您已成功登出系统', life: 3000 })
      router.push('/login')
    } catch (error) {
      console.error('登出失败:', error)
      toast.add({ severity: 'error', summary: '登出失败', detail: '请稍后重试', life: 3000 })
    } finally {
      isLoggingOut.value = false
    }
  }

  onMounted(() => {
    fetchSettings()
  })

  return {
    activeSection,
    settingSections,
    isLoadingSettings,
    isSavingSettings,
    isLoggingOut,
    accountSettings,
    parsingSettings,
    exportSettings,
    themeSettings,
    notificationSettings,
    securitySettings,
    watermarkSettings,
    lastLoginTime,
    exportFormats,
    themeColors,
    numberFormatOptions,
    saveAccountSettings,
    saveParsingSettings,
    saveExportSettings,
    applyTheme,
    saveNotificationSettings,
    saveWatermarkSettings,
    logout
  }
}
