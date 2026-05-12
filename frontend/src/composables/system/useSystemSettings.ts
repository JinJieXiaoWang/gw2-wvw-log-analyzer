import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { settingsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { authStore } from '@/composables/system/usePermission'
import { useSettingsStore } from '@/store/system/settings'

export function useSystemSettings() {
  const toast = useToast()
  const router = useRouter()
  const settingsStore = useSettingsStore()

  const isLoadingSettings = ref(false)
  const isSavingSettings = ref(false)
  const isLoggingOut = ref(false)

  const activeSection = ref('account')

  const settingSections = [
    { id: 'account', label: '账号设置', icon: 'pi pi-user' },
    { id: 'parsing', label: '解析参数', icon: 'pi pi-sliders-h' },
    { id: 'export', label: '导出格式', icon: 'pi pi-file-export' },
    { id: 'theme', label: '界面主题', icon: 'pi pi-palette' },
    { id: 'notifications', label: '通知设置', icon: 'pi pi-bell' },
    { id: 'scoring-rules', label: '评分规则', icon: 'pi pi-chart-line', isExternal: true, path: '/scoring-rules' },
    { id: 'profession-mgmt', label: '职业管理', icon: 'pi pi-users', isExternal: true, path: '/professions' },
    { id: 'system-params', label: '系统参数', icon: 'pi pi-database' },
    { id: 'dictionary', label: '字典管理', icon: 'pi pi-book' },
    { id: 'security', label: '安全设置', icon: 'pi pi-shield' },
    { id: 'watermark', label: '水印设置', icon: 'pi pi-circle-on' }
  ]

  const accountSettings = reactive({
    username: 'Admin',
    email: 'admin@example.com',
    bio: 'WVW战场数据分析师'
  })

  const parsingSettings = reactive({
    includeOverkill: true,
    ignoreSmallDamage: true,
    preFightBuffer: 5,
    autoCategorizeSkills: true
  })

  const exportSettings = reactive({
    defaultFormat: 'csv',
    includeHeader: true,
    utf8Encoding: true,
    numberFormat: 'auto'
  })

  const themeSettings = reactive({
    mode: 'dark',
    primaryColor: '#165DFF',
    zoom: 100
  })

  const notificationSettings = reactive({
    email: true,
    push: false,
    parseComplete: true
  })

  const securitySettings = reactive({
    twoFactorAuth: false
  })

  const watermarkSettings = reactive({
    watermarkEnabled: settingsStore.settings.watermarkEnabled,
    watermarkText: settingsStore.settings.watermarkText,
    watermarkScreenshotEnabled: settingsStore.settings.watermarkScreenshotEnabled
  })

  const lastLoginTime = ref('2024-01-15 14:30:00')

  const exportFormats = [
    { id: 'csv', label: 'CSV', icon: 'pi pi-file', color: '#00B42A' },
    { id: 'excel', label: 'Excel', icon: 'pi pi-file-excel', color: '#00B42A' },
    { id: 'json', label: 'JSON', icon: 'pi pi-code', color: '#165DFF' },
    { id: 'pdf', label: 'PDF', icon: 'pi pi-file-pdf', color: '#F53F3F' }
  ]

  const themeColors = [
    { id: 'blue', value: '#165DFF' },
    { id: 'purple', value: '#722ED1' },
    { id: 'green', value: '#00B42A' },
    { id: 'orange', value: '#FF7D00' },
    { id: 'red', value: '#F53F3F' }
  ]

  const numberFormatOptions = [
    { label: '自动', value: 'auto' },
    { label: '千位分隔符 (1,000)', value: 'comma' },
    { label: '科学计数法 (1.0e6)', value: 'scientific' }
  ]

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

  const saveAccountSettings = () => {
    toast.add({ severity: 'success', summary: '保存成功', detail: '账号设置已保存', life: 3000 })
  }

  const saveParsingSettings = () => {
    toast.add({ severity: 'success', summary: '保存成功', detail: '解析参数已保存', life: 3000 })
  }

  const saveExportSettings = () => {
    toast.add({ severity: 'success', summary: '保存成功', detail: '导出格式已保存', life: 3000 })
    saveSettings()
  }

  const applyTheme = () => {
    toast.add({ severity: 'success', summary: '应用成功', detail: '主题已应用', life: 3000 })
    saveSettings()
  }

  const saveNotificationSettings = () => {
    toast.add({ severity: 'success', summary: '保存成功', detail: '通知设置已保存', life: 3000 })
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
