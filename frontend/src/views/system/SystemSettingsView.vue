<template>
  <div class="space-y-6">
    <PageHeader
      title="系统设置"
      subtitle="管理系统配置、个人设置和系统字典"
      icon="pi pi-cog"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <div class="lg:col-span-1">
        <SettingSidebar
          :active-section="activeSection"
          :setting-sections="settingSections"
          @select-section="activeSection = $event"
        />
      </div>

      <div class="lg:col-span-3 min-h-[400px]">
        <transition
          :key="activeSection"
          name="setting-section"
          mode="out-in"
          appear
        >
          <AccountSettings
            v-if="activeSection === 'account'"
            :key="'account'"
            :account-settings="accountSettings"
            @save-account-settings="saveAccountSettings"
          />
          <ParsingSettings
            v-else-if="activeSection === 'parsing'"
            :key="'parsing'"
            :parsing-settings="parsingSettings"
            @save-parsing-settings="saveParsingSettings"
          />
          <ExportSettings
            v-else-if="activeSection === 'export'"
            :key="'export'"
            :export-settings="exportSettings"
            :export-formats="exportFormats"
            :number-format-options="numberFormatOptions"
            @save-export-settings="saveExportSettings"
          />
          <ThemeSettings
            v-else-if="activeSection === 'theme'"
            :key="'theme'"
            :theme-settings="themeSettings"
            :theme-colors="themeColors"
            @apply-theme="applyTheme"
          />
          <NotificationSettings
            v-else-if="activeSection === 'notifications'"
            :key="'notifications'"
            :notification-settings="notificationSettings"
            @save-notification-settings="saveNotificationSettings"
          />
          <div
            v-else-if="activeSection === 'dictionary'"
            :key="'dictionary'"
            class="dictionary-embedded-container"
          >
            <DictionaryManagementWrapper :is-embedded="true" />
          </div>
          <SystemParamsSettings
            v-else-if="activeSection === 'system-params'"
            :key="'system-params'"
          />
          <SecuritySettings
            v-else-if="activeSection === 'security'"
            :key="'security'"
            :security-settings="securitySettings"
            :last-login-time="lastLoginTime"
            @logout="logout"
          />
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
import DictionaryManagementWrapper from '@/components/common/dictionary/DictionaryManagementWrapper.vue'
import SettingSidebar from '@/components/settings/SettingSidebar.vue'
import AccountSettings from '@/components/settings/account/AccountSettings.vue'
import ExportSettings from '@/components/settings/account/ExportSettings.vue'
import SecuritySettings from '@/components/settings/account/SecuritySettings.vue'
import NotificationSettings from '@/components/settings/appearance/NotificationSettings.vue'
import ThemeSettings from '@/components/settings/appearance/ThemeSettings.vue'
import WatermarkSettings from '@/components/settings/appearance/WatermarkSettings.vue'
import SystemParamsSettings from '@/components/settings/system/SystemParamsSettings.vue'
import ParsingSettings from '@/components/settings/upload/ParsingSettings.vue'
import { useSystemSettings } from '@/composables/system/useSystemSettings'
import PageHeader from '@/layout/components/PageHeader.vue'
import Toast from 'primevue/toast'

const {
  activeSection,
  settingSections,
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
} = useSystemSettings()
</script>

<style scoped>
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

.dictionary-embedded-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>
