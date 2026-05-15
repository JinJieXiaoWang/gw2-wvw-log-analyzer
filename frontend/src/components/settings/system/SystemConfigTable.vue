<template>
  <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-gray-600 to-gray-800 flex items-center justify-center">
          <i class="pi pi-database text-white" />
        </div>
        <div>
          <h4 class="font-semibold text-color">
            所有配置项
          </h4>
          <span class="text-xs text-color-secondary">查看和编辑所有系统配置</span>
        </div>
      </div>
      <BaseButton
        :label="expanded ? '收起' : '展开全部'"
        :icon="expanded ? 'pi pi-angle-up' : 'pi pi-angle-down'"
        text
        size="small"
        @click="emit('toggle')"
      />
    </div>
    <DataTable
      v-if="expanded"
      :value="configs"
      :loading="loading"
      striped-rows
      size="small"
      class="p-datatable-sm"
    >
      <Column
        field="config_name"
        header="配置名称"
        style="width: 200px"
      >
        <template #body="{ data }">
          <div>
            <span class="font-medium text-color">{{ data.config_name }}</span>
            <p class="text-xs text-color-secondary mt-0.5">
              {{ data.config_key }}
            </p>
          </div>
        </template>
      </Column>
      <Column
        field="config_value"
        header="配置值"
      >
        <template #body="{ data }">
          <div v-if="data.config_type === YesNo.NO">
            <BaseInput
              v-model="data.config_value"
              class="p-inputtext-sm w-full"
              @blur="emit('update', data)"
            />
          </div>
          <div v-else-if="data.config_type === YesNo.YES && isBoolean(data.config_key)">
            <ToggleSwitch
              :model-value="data.config_value === 'true'"
              @update:model-value="emit('boolChange', data, $event)"
            />
          </div>
          <div v-else>
            <BaseInput
              v-model="data.config_value"
              class="p-inputtext-sm w-full"
              @blur="emit('update', data)"
            />
          </div>
        </template>
      </Column>
      <Column
        field="remark"
        header="说明"
        style="width: 300px"
      >
        <template #body="{ data }">
          <span class="text-xs text-color-secondary">{{ data.remark || '-' }}</span>
        </template>
      </Column>
      <Column
        field="config_type"
        header="类型"
        style="width: 100px"
      >
        <template #body="{ data }">
          <DictTag
            dict-type="sys_yes_no"
            :value="data.config_type"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import DictTag from '@/components/common/dict/DictTag.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import ToggleSwitch from 'primevue/toggleswitch'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { YesNo } from '@/constants/dictValues'

const { configs, loading, expanded } = defineProps<{
  configs: any[]
  loading: boolean
  expanded: boolean
}>()

const emit = defineEmits(['toggle', 'update', 'boolChange'])

const booleanKeys = ['auto_backup', 'watermark_enabled', 'watermark_screenshot_enabled', 'auto_cleanup_enabled']

function isBoolean(key: string) {
  return booleanKeys.includes(key)
}
</script>
