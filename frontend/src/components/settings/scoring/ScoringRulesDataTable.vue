<template>
  <div class="rounded-lg overflow-hidden border border-surface-200 dark:border-surface-700">
    <DataTable
      :value="editableRules"
      :loading="loading"
      striped-rows
      row-hover
      class="text-sm"
    >
      <template #empty>
        <div class="flex flex-col items-center justify-center py-12 text-color-secondary">
          <i class="pi pi-inbox text-5xl mb-4 opacity-50" />
          <p>暂无评分规则，请添加新规则</p>
        </div>
      </template>
      <Column
        field="sort_order"
        header="排序"
        style="width: 80px"
      >
        <template #body="{ index }">
          <div class="flex items-center gap-1">
            <BaseButton
              icon="pi pi-chevron-up"
              text
              rounded
              size="small"
              class="w-7 h-7"
              :disabled="index === 0"
              @click="$emit('moveUp', index)"
            />
            <span class="w-6 text-center text-sm font-semibold">{{ index + 1 }}</span>
            <BaseButton
              icon="pi pi-chevron-down"
              text
              rounded
              size="small"
              class="w-7 h-7"
              :disabled="index === editableRules.length - 1"
              @click="$emit('moveDown', index)"
            />
          </div>
        </template>
      </Column>
      <Column
        field="dimension"
        header="评分维度"
        style="width: 150px"
      >
        <template #body="{ data }">
          <div class="flex items-center gap-3">
            <div
              class="w-9 h-9 rounded-md flex items-center justify-center text-white text-sm shrink-0"
              :style="{ background: getDimensionColor(data.dimension) }"
            >
              <i :class="getDimensionIcon(data.dimension)" />
            </div>
            <span class="font-medium">{{ getDimensionLabel(data.dimension) }}</span>
          </div>
        </template>
      </Column>
      <Column
        field="weight"
        header="权重分配"
        style="min-width: 280px"
      >
        <template #body="{ index }">
          <div class="flex items-center gap-3 relative">
            <Slider
              v-model="editableRules[index].weight"
              :min="0"
              :max="1"
              :step="0.01"
              class="flex-1"
              :disabled="!canWrite"
              @change="$emit('markChanged')"
            />
            <div
              class="flex items-center gap-1 bg-surface-100 dark:bg-surface-800 px-2 py-1 rounded-md border border-surface-200 dark:border-surface-700"
            >
              <InputNumber
                v-model="editableRules[index].weight"
                :min="0"
                :max="10"
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
              :style="{ width: `${editableRules[index].weight * 100}%` }"
            />
          </div>
        </template>
      </Column>
      <Column
        field="description"
        header="规则描述"
      >
        <template #body="{ index }">
          <InputText
            v-model="editableRules[index].description"
            size="small"
            class="w-full"
            placeholder="输入规则描述..."
            :disabled="!canWrite"
            @update:model-value="$emit('markChanged')"
          />
        </template>
      </Column>
      <Column
        field="is_active"
        header="状态"
        style="width: 100px"
      >
        <template #body="{ index }">
          <div class="flex items-center gap-2">
            <ToggleSwitch
              v-model="editableRules[index].is_active"
              :disabled="!canWrite"
              @update:model-value="$emit('markChanged')"
            />
            <span
              class="text-xs font-medium"
              :class="editableRules[index].is_active ? 'text-green-500' : 'text-color-secondary'"
            >
              {{ editableRules[index].is_active ? '启用' : '禁用' }}
            </span>
          </div>
        </template>
      </Column>
      <Column
        header="操作"
        style="width: 80px"
      >
        <template #body="{ index }">
          <BaseButton
            v-if="canWrite"
            icon="pi pi-trash"
            variant="danger"
            text
            rounded
            size="small"
            class="w-9 h-9"
            @click="$emit('remove', index)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Slider from 'primevue/slider'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import ToggleSwitch from 'primevue/toggleswitch'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import type { ScoringRule } from '@/services/core/scoringRulesService'

defineProps<{
  editableRules: ScoringRule[]
  loading: boolean
  canWrite: boolean
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
}>()

defineEmits<{
  moveUp: [index: number]
  moveDown: [index: number]
  remove: [index: number]
  markChanged: []
}>()
</script>
