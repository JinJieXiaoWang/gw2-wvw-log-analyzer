<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <PageHeader
      title="系统设置"
      subtitle="管理系统配置、个人设置和系统字典"
      icon="pi pi-cog"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <!-- 设置内容 -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- 侧边导航 -->
      <div class="lg:col-span-1">
        <SettingSidebar
          :active-section="activeSection"
          :setting-sections="settingSections"
          @select-section="activeSection = $event"
        />
      </div>

      <!-- 设置详情 -->
      <div class="lg:col-span-3 min-h-[400px]">
        <transition
          :key="activeSection"
          name="setting-section"
          mode="out-in"
          appear
        >
          <!-- 账号设置 -->
          <AccountSettings
            v-if="activeSection === 'account'"
            :key="'account'"
            :account-settings="accountSettings"
            @save-account-settings="saveAccountSettings"
          />

          <!-- 解析参数设置 -->
          <ParsingSettings
            v-else-if="activeSection === 'parsing'"
            :key="'parsing'"
            :parsing-settings="parsingSettings"
            @save-parsing-settings="saveParsingSettings"
          />

          <!-- 导出格式设置 -->
          <ExportSettings
            v-else-if="activeSection === 'export'"
            :key="'export'"
            :export-settings="exportSettings"
            :export-formats="exportFormats"
            :number-format-options="numberFormatOptions"
            @save-export-settings="saveExportSettings"
          />

          <!-- 界面主题设置 -->
          <ThemeSettings
            v-else-if="activeSection === 'theme'"
            :key="'theme'"
            :theme-settings="themeSettings"
            :theme-colors="themeColors"
            @apply-theme="applyTheme"
          />

          <!-- 通知设置 -->
          <NotificationSettings
            v-else-if="activeSection === 'notifications'"
            :key="'notifications'"
            :notification-settings="notificationSettings"
            @save-notification-settings="saveNotificationSettings"
          />

          <!-- 字典管理 -->
          <div
            v-else-if="activeSection === 'dictionary'"
            :key="'dictionary'"
          >
            <DictionaryManagementWrapper />
          </div>

          <!-- 评分规则设置 -->
          <ScoringRulesSettings
            v-else-if="activeSection === 'scoring-rules'"
            :key="'scoring-rules'"
          />

          <!-- 安全设置 -->
          <SecuritySettings
            v-else-if="activeSection === 'security'"
            :key="'security'"
            :security-settings="securitySettings"
            :last-login-time="lastLoginTime"
            @logout="logout"
          />

          <!-- 水印设置 -->
          <WatermarkSettings
            v-else-if="activeSection === 'watermark'"
            :key="'watermark'"
            :watermark-settings="watermarkSettings"
            @save-watermark-settings="saveWatermarkSettings"
          />
        </transition>
      </div>
    </div>
  </div>

  <Toast />
</template>

<script setup lang="ts">
/**
 * 设置页面
 * 更新日期：2026-05-04
 */

import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import SettingSidebar from '@/components/settings/SettingSidebar.vue'
import AccountSettings from '@/components/settings/AccountSettings.vue'
import ParsingSettings from '@/components/settings/ParsingSettings.vue'
import ExportSettings from '@/components/settings/ExportSettings.vue'
import ThemeSettings from '@/components/settings/ThemeSettings.vue'
import NotificationSettings from '@/components/settings/NotificationSettings.vue'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'
import WatermarkSettings from '@/components/settings/WatermarkSettings.vue'
import ScoringRulesSettings from '@/components/settings/ScoringRulesSettings.vue'
import DictionaryManagementWrapper from '@/components/common/DictionaryManagementWrapper.vue'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'
import { settingsService } from '@/services'
import { ApiResponseWrapper } from '@/services/core/errorHandler'
import { authStore } from '@/composables/system/usePermission'
import { useSettingsStore } from '@/store/system/settings'

// ============================================
// Toast提示
// ============================================
const toast = useToast()
const router = useRouter()
const settingsStore = useSettingsStore()

// ============================================
// 加载状态
// ============================================
const isLoadingSettings = ref(false)
const isSavingSettings = ref(false)
const isLoggingOut = ref(false)

// ============================================
// 当前激活的设置分区
// ============================================
const activeSection = ref('account')

const settingSections = [
  { id: 'account', label: '账号设置', icon: 'pi pi-user' },
  { id: 'parsing', label: '解析参数', icon: 'pi pi-sliders-h' },
  { id: 'export', label: '导出格式', icon: 'pi pi-file-export' },
  { id: 'theme', label: '界面主题', icon: 'pi pi-palette' },
  { id: 'notifications', label: '通知设置', icon: 'pi pi-bell' },
  { id: 'dictionary', label: '字典管理', icon: 'pi pi-book' },
  { id: 'scoring-rules', label: '评分规则', icon: 'pi pi-chart-line' },
  { id: 'security', label: '安全设置', icon: 'pi pi-shield' },
  { id: 'watermark', label: '水印设置', icon: 'pi pi-circle-on' }
]

// ============================================
// 设置数据
// ============================================
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

// ============================================
// API数据获取函数
// ============================================

/**
 * 获取系统设置
 * API: GET /api/v1/settings
 */
const fetchSettings = async (): Promise<void> => {
  isLoadingSettings.value = true
  try {
    const result = await ApiResponseWrapper.wrap(
      settingsService.getSettings(),
      {
        showErrorMessage: false
      }
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

/**
 * 保存系统设置
 * API: PUT /api/v1/settings
 */
const saveSettings = async (): Promise<void> => {
  isSavingSettings.value = true
  try {
    const settingsData = {
      theme: themeSettings.mode,
      export_format: exportSettings.defaultFormat,
      parse_parallel: parsingSettings.preFightBuffer
    }
    const result = await ApiResponseWrapper.wrap(
      settingsService.updateSettings(settingsData),
      {
        showSuccessMessage: true,
        successMessage: '设置已保存',
        showErrorMessage: true
      }
    )

    if (result.success) {
      // Settings saved successfully
    }
  } finally {
    isSavingSettings.value = false
  }
}

// ============================================
// 生命周期
// ============================================
onMounted(() => {
  fetchSettings()
})

const saveAccountSettings = () => {
  toast.add({
    severity: 'success',
    summary: '保存成功',
    detail: '账号设置已保存',
    life: 3000
  })
}

const saveParsingSettings = () => {
  toast.add({
    severity: 'success',
    summary: '保存成功',
    detail: '解析参数已保存',
    life: 3000
  })
}

const saveExportSettings = () => {
  toast.add({
    severity: 'success',
    summary: '保存成功',
    detail: '导出格式已保存',
    life: 3000
  })
  saveSettings()
}

const applyTheme = () => {
  toast.add({
    severity: 'success',
    summary: '应用成功',
    detail: '主题已应用',
    life: 3000
  })
  saveSettings()
}

const saveNotificationSettings = () => {
  toast.add({
    severity: 'success',
    summary: '保存成功',
    detail: '通知设置已保存',
    life: 3000
  })
}

const saveWatermarkSettings = async (settings: { watermarkEnabled: boolean; watermarkText: string; watermarkScreenshotEnabled: boolean }) => {
  Object.assign(watermarkSettings, settings)
  settingsStore.updateSettings({
    watermarkEnabled: settings.watermarkEnabled,
    watermarkText: settings.watermarkText,
    watermarkScreenshotEnabled: settings.watermarkScreenshotEnabled
  })
  // 同步到后端（全局配置）
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
  toast.add({
    severity: 'success',
    summary: '保存成功',
    detail: '水印设置已保存并同步到服务器',
    life: 3000
  })
}

const logout = async () => {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    toast.add({
      severity: 'success',
      summary: '登出成功',
      detail: '您已成功登出系统',
      life: 3000
    })
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
    toast.add({
      severity: 'error',
      summary: '登出失败',
      detail: '请稍后重试',
      life: 3000
    })
  } finally {
    isLoggingOut.value = false
  }
}
</script>

<style scoped>
/* 设置分区切换动画 */
.setting-section-enter-active,
.setting-section-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.setting-section-enter-from {
  opacity: 0;
  transform: translateX(8px);
}

.setting-section-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}
</style>
