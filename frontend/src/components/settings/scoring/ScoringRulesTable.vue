<template>
  <div class="mb-6">
    <DataTable
      :value="editableRules"
      :loading="loading"
      class="w-full"
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
              @click="$emit('move-up', index)"
            />
            <span class="w-6 text-center text-sm font-medium text-neutral-text">{{ index + 1 }}</span>
            <BaseButton
              icon="pi pi-chevron-down"
              text
              rounded
              size="small"
              :disabled="index === editableRules.length - 1"
              @click="$emit('move-down', index)"
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
        header="Ȩ重"
        style="width: 280px; min-width: 280px;"
      >
        <template #body="{ index }">
          <div class="flex items-center gap-3">
            <div
              class="flex-1"
              style="min-width: 150px; max-width: 180px;"
            >
              <Slider
                v-model="editableRules[index].weight"
                :min="0"
                :max="1"
                :step="0.01"
                class="w-full"
                @change="$emit('mark-changed')"
              />
            </div>
            <div style="width: 70px; flex-shrink: 0;">
              <BaseInputNumber
                v-model="editableRules[index].weight"
                :min="0"
                :max="1"
                :step="0.01"
                :max-fraction-digits="2"
                size="small"
                class="w-full"
                @update:model-value="$emit('mark-changed')"
              />
            </div>
          </div>
        </template>
      </Column>
      <Column
        header="描述"
        style="flex: 1; min-width: 250px;"
      >
        <template #body="{ index }">
          <BaseInput
            v-model="editableRules[index].description"
            size="small"
            class="w-full"
            placeholder="输入描述..."
            @update:model-value="$emit('mark-changed')"
          />
        </template>
      </Column>
      <Column
        header="״̬"
        style="width: 120px; min-width: 120px;"
      >
        <template #body="{ data, index }">
          <div class="flex items-center gap-2">
            <ToggleSwitch
              v-model="editableRules[index].is_active"
              @update:model-value="$emit('mark-changed')"
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

defineProps<{
  editableRules: ScoringRule[]
  loading: boolean
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
}>()

defineEmits<{
  'move-up': [index: number]
  'move-down': [index: number]
  'remove': [index: number]
  'mark-changed': []
}>()
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
