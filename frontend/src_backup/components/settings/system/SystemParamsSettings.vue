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
        class="btn-game"
        @click="saveAllConfigs"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <i class="pi pi-cog text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">核心功能</h4>
            <span class="text-xs text-color-secondary">影响系统核心行为</span>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded flex items-center justify-center bg-blue-100 dark:bg-blue-900/30">
                <i class="pi pi-chart-line text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">评分模式</label>
                <p class="text-xs text-color-secondary">选择评分规则的应用方式</p>
              </div>
            </div>
            <BaseSelect
              v-model="localConfigs.scoring_mode"
              :options="scoringModeOptions"
              option-label="label"
              option-value="value"
              class="w-40"
              @change="markChanged('scoring_mode')"
            />
          </div>
          <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded flex items-center justify-center bg-green-100 dark:bg-green-900/30">
                <i class="pi pi-server text-green-600 dark:text-green-400" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">默认服务器</label>
                <p class="text-xs text-color-secondary">新建日志时默认选中的服务器</p>
              </div>
            </div>
            <BaseInput
              v-model="localConfigs.default_server"
              class="w-40"
              @input="markChanged('default_server')"
            />
          </div>
        </div>
      </div>

      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
            <i class="pi pi-bolt text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">解析参数</h4>
            <span class="text-xs text-color-secondary">日志解析相关配置</span>
          </div>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded flex items-center justify-center bg-purple-100 dark:bg-purple-900/30">
                <i class="pi pi-spinner text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">解析并行数</label>
                <p class="text-xs text-color-secondary">批量解析时的并行任务数</p>
              </div>
            </div>
            <BaseInputNumber
              v-model="localConfigs.parse_parallel"
              :min="1"
              :max="8"
              class="w-24"
              @blur="markChanged('parse_parallel')"
            />
          </div>
          <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded flex items-center justify-center bg-teal-100 dark:bg-teal-900/30">
                <i class="pi pi-calendar text-teal-600 dark:text-teal-400" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">数据保留天数</label>
                <p class="text-xs text-color-secondary">超过此天数的日志将被清理</p>
              </div>
            </div>
            <BaseInputNumber
              v-model="localConfigs.retention_days"
              :min="30"
              :max="3650"
              suffix=" 天"
              class="w-32"
              @blur="markChanged('retention_days')"
            />
          </div>
        </div>
      </div>

      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <i class="pi pi-file-export text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">导出格式</h4>
            <span class="text-xs text-color-secondary">数据导出的默认格式</span>
          </div>
        </div>
        <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded flex items-center justify-center bg-cyan-100 dark:bg-cyan-900/30">
              <i class="pi pi-file text-cyan-600 dark:text-cyan-400" />
            </div>
            <div>
              <label class="text-sm font-medium text-color">默认导出格式</label>
              <p class="text-xs text-color-secondary">选择默认的数据导出格式</p>
            </div>
          </div>
          <BaseSelect
            v-model="localConfigs.export_format"
            :options="exportFormatOptions"
            option-label="label"
            option-value="value"
            class="w-32"
            @change="markChanged('export_format')"
          />
        </div>
      </div>

      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-pink-600 flex items-center justify-center">
            <i class="pi pi-database text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">系统维护</h4>
            <span class="text-xs text-color-secondary">数据备份与维护设置</span>
          </div>
        </div>
        <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded flex items-center justify-center bg-red-100 dark:bg-red-900/30">
              <i class="pi pi-history text-red-600 dark:text-red-400" />
            </div>
            <div>
              <label class="text-sm font-medium text-color">自动备份</label>
              <p class="text-xs text-color-secondary">是否启用自动数据库备份</p>
            </div>
          </div>
          <ToggleSwitch
            v-model="localConfigs.auto_backup"
            @change="markChanged('auto_backup')"
          />
        </div>
      </div>

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
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { usePermission } from '@/composables/system/usePermission'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import ToggleSwitch from 'primevue/toggleswitch'
import SystemConfigTable from './SystemConfigTable.vue'
import UploadParseParamsPanel from '../upload/UploadParseParamsPanel.vue'
import CacheCleanupParamsPanel from './CacheCleanupParamsPanel.vue'
import { settingsService } from '@/services'

const toast = useToast()
const { can } = usePermission()
const canWrite = can('write')

const loading = ref(false)
const saving = ref(false)
const showAllConfigs = ref(false)
const originalConfigs = ref<Record<string, string>>({})
const allConfigs = ref<any[]>([])
const changedConfigs = ref<Set<string>>(new Set())

const localConfigs = reactive({
  scoring_mode: 'role_based',
  default_server: 'Tarnished Coast',
  parse_parallel: 1,
  retention_days: 365,
  export_format: 'json',
  auto_backup: true,
  upload_max_file_size: 50,
  upload_allowed_extensions: '[".zevtc", ".evtc"]',
  analysis_max_fight_duration: 3600,
  cache_menu_ttl: 3600,
  auto_cleanup_enabled: true,
  auto_cleanup_retention_days: 30,
})

const scoringModeOptions = [
  { label: '角色定位评分', value: 'role_based' },
  { label: '职业评分', value: 'profession_based' },
]
const exportFormatOptions = [
  { label: 'JSON', value: 'json' },
  { label: 'CSV', value: 'csv' },
  { label: 'Excel', value: 'xlsx' },
]

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
        const numericKeys = ['parse_parallel', 'retention_days', 'upload_max_file_size', 'analysis_max_fight_duration', 'cache_menu_ttl', 'auto_cleanup_retention_days']
        const booleanKeys = ['auto_backup', 'auto_cleanup_enabled']
        if (numericKeys.includes(config.config_key)) {
          (localConfigs as any)[config.config_key] = parseInt(config.config_value) || 0
        } else if (booleanKeys.includes(config.config_key)) {
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

onMounted(() => loadConfigs())
</script>

<style scoped>
</style>
