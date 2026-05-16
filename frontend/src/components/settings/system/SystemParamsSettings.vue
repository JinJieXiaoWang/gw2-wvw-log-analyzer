<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-semibold text-color flex items-center gap-2">
          <i class="pi pi-sliders-h text-primary-500" /> 系统参数配置
        </h3>
        <p class="text-sm text-color-secondary mt-1">
          管理系统核心配置项，包括评分模式、解析参数等功能开关
        </p>
      </div>
      <BaseButton
        v-if="canWrite"
        label="保存更改"
        icon="pi pi-save"
        :loading="saving"
        :disabled="!hasChanges"
        @click="saveAllConfigs"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <SystemParamsCoreFeatures
        :configs="localConfigs"
        :scoring-mode-options="scoringModeOptions"
        @mark-changed="markChanged"
      />
      <SystemParamsParseSettings
        :configs="localConfigs"
        @mark-changed="markChanged"
      />
      <SystemParamsExportSettings
        :configs="localConfigs"
        :export-format-options="exportFormatOptions"
        @mark-changed="markChanged"
      />
      <SystemParamsMaintenance
        :configs="localConfigs"
        @mark-changed="markChanged"
      />
      <UploadParseParamsPanel
        :configs="localConfigs"
        @mark-changed="markChanged"
      />
      <CacheCleanupParamsPanel
        :configs="localConfigs"
        @mark-changed="markChanged"
      />
    </div>

    <SystemConfigTable
      :configs="allConfigs"
      :loading="loading"
      :expanded="showAllConfigs"
      @toggle="showAllConfigs = !showAllConfigs"
      @update="updateConfig"
      @bool-change="handleBooleanChange"
    />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { usePermission } from '@/composables/system/usePermission'
import {
  BOOLEAN_CONFIG_KEYS,
  EXPORT_FORMAT_SELECT_OPTIONS,
  NUMERIC_CONFIG_KEYS,
  SCORING_MODE_OPTIONS,
  SYSTEM_CONFIG_DEFAULTS
} from '@/config/settings'
import { useDictOptions } from '@/composables/system/useDictOptions'
import { settingsService } from '@/services'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import UploadParseParamsPanel from '../upload/UploadParseParamsPanel.vue'
import CacheCleanupParamsPanel from './CacheCleanupParamsPanel.vue'
import SystemConfigTable from './SystemConfigTable.vue'
import SystemParamsCoreFeatures from './SystemParamsCoreFeatures.vue'
import SystemParamsParseSettings from './SystemParamsParseSettings.vue'
import SystemParamsExportSettings from './SystemParamsExportSettings.vue'
import SystemParamsMaintenance from './SystemParamsMaintenance.vue'

const toast = useToast()
const { can } = usePermission()
const canWrite = can('write')

const loading = ref(false)
const saving = ref(false)
const showAllConfigs = ref(false)
const originalConfigs = ref<Record<string, string>>({})
const allConfigs = ref<any[]>([])
const changedConfigs = ref<Set<string>>(new Set())

const localConfigs = reactive({ ...SYSTEM_CONFIG_DEFAULTS })

const { options: scoringModeOptions, loadOptions: loadScoringModes } = useDictOptions('scoring_mode', false, SCORING_MODE_OPTIONS as any)
const { options: exportFormatOptions, loadOptions: loadExportFormats } = useDictOptions('export_format', false, EXPORT_FORMAT_SELECT_OPTIONS as any)

const hasChanges = computed(() => changedConfigs.value.size > 0)

function markChanged(key: string) { changedConfigs.value.add(key) }

async function loadConfigs() {
  loading.value = true
  try {
    const configs = await settingsService.getSystemSettings()
    allConfigs.value = configs
    for (const config of configs) {
      originalConfigs.value[config.config_key] = config.config_value
      if (config.config_key in localConfigs) {
        if (NUMERIC_CONFIG_KEYS.includes(config.config_key)) {
          (localConfigs as any)[config.config_key] = parseInt(config.config_value) || 0
        } else if (BOOLEAN_CONFIG_KEYS.includes(config.config_key)) {
          (localConfigs as any)[config.config_key] = config.config_value === 'true'
        } else {
          (localConfigs as any)[config.config_key] = config.config_value
        }
      }
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: '错误', detail: '加载系统配置失败', life: 3000 })
  } finally {
    loading.value = false
  }
}

async function updateConfig(config: any) {
  try {
    await settingsService.updateSystemSetting(config.config_key, config.config_value)
    toast.add({ severity: 'success', summary: '成功', detail: `配置「${config.config_name}」已更新`, life: 2000 })
  } catch {
    toast.add({ severity: 'error', summary: '错误', detail: `保存「${config.config_name}」失败`, life: 3000 })
  }
}

async function saveAllConfigs() {
  saving.value = true
  try {
    const promises: Promise<any>[] = []
    for (const key of changedConfigs.value) {
      let value = (localConfigs as any)[key]
      if (typeof value === 'boolean') value = value.toString()
      promises.push(settingsService.updateSystemSetting(key, value))
    }
    await Promise.all(promises)
    changedConfigs.value.clear()
    toast.add({ severity: 'success', summary: '成功', detail: '所有配置已保存', life: 2000 })
  } catch {
    toast.add({ severity: 'error', summary: '错误', detail: '保存配置失败', life: 3000 })
  } finally {
    saving.value = false
  }
}

function handleBooleanChange(config: any, value: boolean) {
  config.config_value = value.toString()
  markChanged(config.config_key)
}

onMounted(() => {
  loadConfigs()
  loadScoringModes()
  loadExportFormats()
})
</script>
