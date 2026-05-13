<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
        <i class="pi pi-trash text-white" />
      </div>
      <div>
        <h4 class="font-semibold text-color">
          缓存与清理
        </h4>
        <span class="text-xs text-color-secondary">菜单缓存与日志自动清理</span>
      </div>
    </div>
    <div class="space-y-4">
      <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-emerald-100 dark:bg-emerald-900/30">
            <i class="pi pi-bars text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">菜单缓存时长</label>
            <p class="text-xs text-color-secondary">
              菜单数据缓存的有效时间
            </p>
          </div>
        </div>
        <BaseInputNumber
          v-model="localConfigs.cache_menu_ttl"
          :min="60"
          :max="86400"
          suffix=" 秒"
          class="w-32"
          @blur="markChanged('cache_menu_ttl')"
        />
      </div>
      <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-emerald-100 dark:bg-emerald-900/30">
            <i class="pi pi-sync text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">自动清理</label>
            <p class="text-xs text-color-secondary">
              是否启用日志自动清理
            </p>
          </div>
        </div>
        <ToggleSwitch
          v-model="localConfigs.auto_cleanup_enabled"
          @change="markChanged('auto_cleanup_enabled')"
        />
      </div>
      <div class="flex items-center justify-between p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-emerald-100 dark:bg-emerald-900/30">
            <i class="pi pi-calendar text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">清理保留天数</label>
            <p class="text-xs text-color-secondary">
              自动清理时保留的日志天数
            </p>
          </div>
        </div>
        <BaseInputNumber
          v-model="localConfigs.auto_cleanup_retention_days"
          :min="1"
          :max="365"
          suffix=" 天"
          class="w-32"
          @blur="markChanged('auto_cleanup_retention_days')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import ToggleSwitch from 'primevue/toggleswitch'
import { reactive, watch } from 'vue'

const props = defineProps<{
  configs: Record<string, any>
}>()

const emit = defineEmits<{
  markChanged: [key: string]
  'update:configs': [configs: Record<string, any>]
}>()

const localConfigs = reactive({ ...props.configs })

watch(() => props.configs, (val) => {
  Object.assign(localConfigs, val)
}, { deep: true })

watch(localConfigs, (val) => {
  emit('update:configs', { ...val })
}, { deep: true })

const markChanged = (key: string) => emit('markChanged', key)
</script>
