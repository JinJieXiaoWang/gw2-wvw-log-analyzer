<template>
  <div class="rounded-lg overflow-hidden border border-surface-200 dark:border-surface-700">
    <DataTable
      :value="localEditableRules"
      :loading="loading"
      class="w-full text-sm"
      :striped-rows="true"
      :row-hover="true"
      :responsive="true"
      :resizable-columns="true"
      scrollable
      scroll-height="auto"
    >
      <Column
        header="排序"
        style="width: 80px; min-width: 80px;"
      >
        <template #body="{ index }">
          <div class="flex items-center gap-1">
            <BaseButton
              icon="pi pi-chevron-up"
              text
              rounded
              size="small"
              :disabled="index === 0"
              @click="$emit('moveUp', index)"
            />
            <span class="w-6 text-center text-sm font-medium text-neutral-text">{{ index + 1 }}</span>
            <BaseButton
              icon="pi pi-chevron-down"
              text
              rounded
              size="small"
              :disabled="index === localEditableRules.length - 1"
              @click="$emit('moveDown', index)"
            />
          </div>
        </template>
      </Column>
      <Column
        header="评分维度"
        style="width: 150px; min-width: 150px;"
      >
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <div
              class="w-7 h-7 rounded-md flex items-center justify-center text-white text-xs"
              :style="{ background: getDimensionColor(data.dimension) }"
            >
              <i :class="getDimensionIcon(data.dimension)" />
            </div>
            <span class="text-sm font-medium text-neutral-text">{{ getDimensionLabel(data.dimension) }}</span>
          </div>
        </template>
      </Column>
      <Column
        header="权重"
        style="width: 280px; min-width: 280px;"
      >
        <template #body="{ index }">
          <div class="flex items-center gap-3 relative">
            <div
              class="flex-1"
              style="min-width: 150px; max-width: 180px;"
            >
              <Slider
                v-model="localEditableRules[index].weight"
                :min="0"
                :max="1"
                :step="0.01"
                class="w-full"
                :disabled="!canWrite"
                @change="$emit('markChanged')"
              />
            </div>
            <div
              class="flex items-center gap-1 bg-surface-100 dark:bg-surface-800 px-2 py-1 rounded-md border border-surface-200 dark:border-surface-700"
            >
              <BaseInputNumber
                v-model="localEditableRules[index].weight"
                :min="0"
                :max="1"
                :step="0.01"
                :max-fraction-digits="2"
                size="small"
                class="w-16"
                :disabled="!canWrite"
                @update:model-value="$emit('markChanged')"
              />
              <span class="text-xs text-color-secondary">%</span>
            </div>
            <div
              class="absolute bottom-0 left-0 h-0.5 bg-primary-500 opacity-30 transition-all"
              :style="{ width: `${localEditableRules[index].weight * 100}%` }"
            />
          </div>
        </template>
      </Column>
      <Column
        header="描述"
        style="flex: 1; min-width: 250px;"
      >
        <template #body="{ index }">
          <BaseInput
            v-model="localEditableRules[index].description"
            size="small"
            class="w-full"
            placeholder="输入描述..."
            :disabled="!canWrite"
            @update:model-value="$emit('markChanged')"
          />
        </template>
      </Column>
      <Column
        header="状态"
        style="width: 120px; min-width: 120px;"
      >
        <template #body="{ data, index }">
          <div class="flex items-center gap-2">
            <ToggleSwitch
              v-model="localEditableRules[index].is_active"
              :disabled="!canWrite"
              @update:model-value="$emit('markChanged')"
            />
            <span
              class="text-xs font-medium"
              :class="data.is_active ? 'text-success' : 'text-neutral-text-tertiary'"
            >{{ data.is_active ? '启用' : '禁用' }}</span>
          </div>
        </template>
      </Column>
      <Column
        header="操作"
        style="width: 60px; min-width: 60px;"
      >
        <template #body="{ index }">
          <BaseButton
            v-if="canWrite"
            icon="pi pi-trash"
            severity="danger"
            text
            rounded
            size="small"
            @click="$emit('remove', index)"
          />
        </template>
      </Column>
      <template #empty>
        <EmptyState
          icon="pi pi-inbox"
          title="暂无评分规则"
          description="请添加新规则"
        />
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import EmptyState from '@/components/common/ui/display/EmptyState.vue'
import type { ScoringRule } from '@/services/core/scoringRulesService'
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  editableRules: ScoringRule[]
  loading: boolean
  canWrite?: boolean
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
  // 兼容旧版调用（ScoringRulesSettings.vue）的额外属性，不实际使用
  totalWeight?: number
  availableDimensions?: any[]
  newDimension?: string
  newWeight?: number
  newDesc?: string
  hasChanges?: boolean
}>(), {
  canWrite: true,
})

const emit = defineEmits<{
  moveUp: [index: number]
  moveDown: [index: number]
  remove: [index: number]
  markChanged: []
  // 兼容旧版调用（ScoringRulesSettings.vue）的额外事件，不实际触发
  add: []
  reset: []
  cancel: []
  save: []
  'update:editableRules': [editableRules: ScoringRule[]]
}>()

const localEditableRules = ref([...props.editableRules])

watch(() => props.editableRules, (val) => {
  localEditableRules.value = [...val]
}, { deep: true })

watch(localEditableRules, (val) => {
  emit('update:editableRules', [...val])
}, { deep: true })
</script>

<style scoped>
:deep(.p-datatable-scrollable-body) { scrollbar-width: thin; scrollbar-color: var(--color-neutral-border) transparent; }
:deep(.p-datatable-scrollable-body::-webkit-scrollbar) { width: 6px; height: 6px; }
:deep(.p-datatable-scrollable-body::-webkit-scrollbar-track) { background: transparent; }
:deep(.p-datatable-scrollable-body::-webkit-scrollbar-thumb) { background-color: var(--color-neutral-border); border-radius: 3px; }
:deep(.p-datatable .p-datatable-tbody > tr > td) { padding: 12px 16px; }
:deep(.p-datatable .p-datatable-thead > tr > th) { padding: 12px 16px; background: var(--color-bg-secondary); border-bottom: 2px solid var(--color-neutral-border); font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-neutral-text-secondary); }
:deep(.p-datatable .p-datatable-tbody > tr:hover) { background-color: var(--color-bg-secondary); }
:deep(.p-datatable .p-datatable-tbody > tr.p-datatable-striped-row) { background-color: var(--color-card); }
:deep(.p-datatable .p-datatable-tbody > tr.p-datatable-striped-row:hover) { background-color: var(--color-bg-secondary); }
</style>
