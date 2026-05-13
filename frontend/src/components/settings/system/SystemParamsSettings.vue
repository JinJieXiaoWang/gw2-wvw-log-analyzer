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
      <!-- 核心功能卡片 -->
      <div class="config-card">
        <div class="card-header">
          <div class="icon-box icon-primary">
            <i class="pi pi-cog text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">
              核心功能
            </h4>
            <span class="text-xs text-color-secondary">影响系统核心行为</span>
          </div>
        </div>
        <div class="space-y-4">
          <div class="config-row">
            <div class="config-info">
              <div class="icon-badge icon-blue">
                <i class="pi pi-chart-line" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">评分模式</label>
                <p class="text-xs text-color-secondary">
                  选择评分规则的应用方式
                </p>
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
          <div class="config-row">
            <div class="config-info">
              <div class="icon-badge icon-green">
                <i class="pi pi-server" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">默认服务器</label>
                <p class="text-xs text-color-secondary">
                  新建日志时默认选中的服务器
                </p>
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

      <!-- 解析参数卡片 -->
      <div class="config-card">
        <div class="card-header">
          <div class="icon-box icon-amber">
            <i class="pi pi-bolt text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">
              解析参数
            </h4>
            <span class="text-xs text-color-secondary">日志解析相关配置</span>
          </div>
        </div>
        <div class="space-y-4">
          <div class="config-row">
            <div class="config-info">
              <div class="icon-badge icon-purple">
                <i class="pi pi-spinner" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">解析并行数</label>
                <p class="text-xs text-color-secondary">
                  批量解析时的并行任务数
                </p>
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
          <div class="config-row">
            <div class="config-info">
              <div class="icon-badge icon-teal">
                <i class="pi pi-calendar" />
              </div>
              <div>
                <label class="text-sm font-medium text-color">数据保留天数</label>
                <p class="text-xs text-color-secondary">
                  超过此天数的日志将被清理
                </p>
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

      <!-- 导出格式卡片 -->
      <div class="config-card">
        <div class="card-header">
          <div class="icon-box icon-cyan">
            <i class="pi pi-file-export text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">
              导出格式
            </h4>
            <span class="text-xs text-color-secondary">数据导出的默认格式</span>
          </div>
        </div>
        <div class="config-row">
          <div class="config-info">
            <div class="icon-badge icon-cyan">
              <i class="pi pi-file" />
            </div>
            <div>
              <label class="text-sm font-medium text-color">默认导出格式</label>
              <p class="text-xs text-color-secondary">
                选择默认的数据导出格式
              </p>
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

      <!-- 系统维护卡片 -->
      <div class="config-card">
        <div class="card-header">
          <div class="icon-box icon-red">
            <i class="pi pi-database text-white" />
          </div>
          <div>
            <h4 class="font-semibold text-color">
              系统维护
            </h4>
            <span class="text-xs text-color-secondary">数据备份与维护设置</span>
          </div>
        </div>
        <div class="config-row">
          <div class="config-info">
            <div class="icon-badge icon-red">
              <i class="pi pi-history" />
            </div>
            <div>
              <label class="text-sm font-medium text-color">自动备份</label>
              <p class="text-xs text-color-secondary">
                是否启用自动数据库备份
              </p>
            </div>
          </div>
          <BaseToggleSwitch
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
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import BaseToggleSwitch from '@/components/common/ui/input/BaseToggleSwitch.vue'
import { usePermission } from '@/composables/system/usePermission'
import {
    BOOLEAN_CONFIG_KEYS,
    EXPORT_FORMAT_SELECT_OPTIONS,
    NUMERIC_CONFIG_KEYS,
    SCORING_MODE_OPTIONS,
    SYSTEM_CONFIG_DEFAULTS
} from '@/constants/settings'
import { useDictOptions } from '@/composables/system/useDictOptions'
import { settingsService } from '@/services'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import UploadParseParamsPanel from '../upload/UploadParseParamsPanel.vue'
import CacheCleanupParamsPanel from './CacheCleanupParamsPanel.vue'
import SystemConfigTable from './SystemConfigTable.vue'

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

<style scoped>
.config-card {
  @apply bg-neutral-card border border-neutral-border rounded-2xl p-5 shadow-sm;
}

.card-header {
  @apply flex items-center gap-3 mb-4;
}

.config-row {
  @apply flex items-center justify-between p-3 bg-neutral-bg-secondary rounded-lg;
}

.config-info {
  @apply flex items-center gap-3;
}

.icon-box {
  @apply w-10 h-10 rounded-lg flex items-center justify-center;
}

.icon-primary {
  @apply bg-gradient-to-br from-primary to-secondary;
}

.icon-amber {
  @apply bg-gradient-to-br from-amber-500 to-orange-600;
}

.icon-cyan {
  @apply bg-gradient-to-br from-cyan-500 to-blue-600;
}

.icon-red {
  @apply bg-gradient-to-br from-red-500 to-pink-600;
}

.icon-badge {
  @apply w-8 h-8 rounded flex items-center justify-center;
}

.icon-blue {
  background-color: var(--color-primary-alpha-10);
  color: var(--color-primary);
}

.icon-green {
  background-color: var(--color-success-alpha-10);
  color: var(--color-success);
}

.icon-purple {
  background-color: var(--color-secondary-alpha-10);
  color: var(--color-secondary);
}

.icon-teal {
  background-color: var(--color-ai-alpha-10);
  color: var(--color-ai);
}

.icon-cyan {
  background-color: var(--color-ai-alpha-10);
  color: var(--color-ai);
}

.icon-red {
  background-color: var(--color-error-alpha-10);
  color: var(--color-error);
}
</style>
