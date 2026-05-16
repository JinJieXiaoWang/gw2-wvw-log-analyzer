<template>
  <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-6 shadow-lg">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-5">
      <div class="flex items-center gap-4">
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center text-xl text-white shadow-lg shrink-0"
          :style="{ background: `linear-gradient(135deg, ${data.roleColor}, ${data.roleGradient})`, boxShadow: `0 8px 24px -8px ${data.roleColor}` }"
        >
          <i :class="data.activeRoleIcon" />
        </div>
        <div>
          <h3 class="text-xl font-semibold text-color">
            {{ data.activeRoleLabel }}评分规则<span
              v-if="data.ruleScope === 'profession' && data.selectedProfession"
              class="text-sm font-normal text-color-secondary ml-2"
            >— {{ data.selectedProfession }}</span>
          </h3>
          <div class="flex items-center gap-3 mt-1 flex-wrap">
            <span class="text-sm text-color-secondary">权重总和</span>
            <div
              class="flex items-baseline gap-1 px-3 py-0.5 rounded-full text-sm font-bold transition-colors"
              :class="data.weightStatusClass === 'optimal' ? 'bg-green-500/10 text-green-500' : data.weightStatusClass === 'warning' ? 'bg-orange-500/10 text-orange-500' : 'bg-red-500/10 text-red-500'"
            >
              <span class="text-base">{{ data.totalWeight.toFixed(2) }}</span><span
                class="text-xs font-normal opacity-60"
              >/ 1.00</span>
            </div>
            <span
              v-if="data.weightStatusClass !== 'optimal'"
              class="flex items-center gap-1 text-xs text-orange-500"
            >
              <i class="pi pi-exclamation-circle" />建议调整至 1.0
            </span>
          </div>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <BaseButton
          v-if="data.ruleScope === 'generic'"
          label="应用到历史数据"
          icon="pi pi-history"
          severity="info"
          outlined
          :loading="data.recalculating"
          :disabled="!data.canRecalculate"
          @click="emit('recalculate')"
        />
        <BaseButton
          v-if="data.ruleScope === 'profession'"
          label="删除职业规则"
          icon="pi pi-trash"
          severity="danger"
          outlined
          :loading="data.deletingProfession"
          :disabled="!data.currentProfessionHasRules"
          @click="emit('delete-profession')"
        />
        <BaseButton
          label="重置默认"
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          :loading="data.resetting"
          @click="emit('reset')"
        />
        <BaseButton
          label="保存更改"
          icon="pi pi-save"
          severity="primary"
          :loading="data.saving"
          :disabled="!data.hasUnsavedChanges"
          @click="emit('save')"
        />
      </div>
    </div>

    <!-- 权重条 -->
    <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full mb-5 overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="data.weightStatusClass === 'optimal' ? 'bg-green-500' : data.weightStatusClass === 'warning' ? 'bg-orange-500' : 'bg-red-500'"
        :style="{ width: `${Math.min(data.totalWeight * 100, 100)}%` }"
      />
      <div
        class="absolute top-0 bottom-0 w-0.5 bg-white/50"
        style="left: 100%"
      />
    </div>

    <ScoringRulesTable
      :editable-rules="data.editableRules"
      :loading="data.loading"
      :can-write="data.canWrite"
      :get-dimension-icon="data.getDimensionIcon"
      :get-dimension-color="data.getDimensionColor"
      :get-dimension-label="data.getDimensionLabel"
      @move-up="emit('move-up', $event)"
      @move-down="emit('move-down', $event)"
      @remove="emit('remove', $event)"
      @mark-changed="emit('mark-changed')"
    />

    <AddRulePanel
      :available-dimensions="data.availableDimensions"
      :active-role="data.activeRole"
      :get-dimension-icon="data.getDimensionIcon"
      :get-dimension-color="data.getDimensionColor"
      :get-dimension-label="data.getDimensionLabel"
      @add-rule="(...args) => emit('add-rule', ...args)"
    />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import ScoringRulesTable from './ScoringRulesTable.vue'
import AddRulePanel from './AddRulePanel.vue'
import type { ScoringRule, DimensionInfo } from '@/services/core/scoringRulesService'

interface RuleEditorData {
  activeRole: string
  activeRoleLabel: string
  activeRoleIcon: string
  roleColor: string
  roleGradient: string
  editableRules: ScoringRule[]
  allDimensions: DimensionInfo[]
  loading: boolean
  saving: boolean
  resetting: boolean
  deletingProfession: boolean
  recalculating: boolean
  canWrite: boolean
  weightStatusClass: string
  totalWeight: number
  ruleScope: string
  selectedProfession: string
  canRecalculate: boolean
  currentProfessionHasRules: boolean
  hasUnsavedChanges: boolean
  availableDimensions: DimensionInfo[]
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
}

const props = defineProps<{ data: RuleEditorData }>()
const emit = defineEmits<{
  save: []
  reset: []
  recalculate: []
  'delete-profession': []
  'add-rule': [dimension: string, weight: number, desc: string]
  'remove': [index: number]
  'move-up': [index: number]
  'move-down': [index: number]
  'mark-changed': []
}>()
</script>

<style scoped>
:deep(.p-slider) {
  background: var(--color-bg-secondary);
  height: 6px;
  border-radius: var(--radius-full);
}

:deep(.p-slider .p-slider-range) {
  background: linear-gradient(90deg, var(--color-primary), var(--color-ai));
  border-radius: var(--radius-full);
}

:deep(.p-slider .p-slider-handle) {
  width: 18px;
  height: 18px;
  background: white;
  border: 3px solid var(--color-primary);
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.4);
  transition: all var(--transition-fast);
}

:deep(.p-slider .p-slider-handle:hover) {
  transform: scale(1.2);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.5);
}

:deep(.p-inputnumber-input) {
  text-align: center;
  font-weight: 600;
  background: transparent;
  border: none;
  color: var(--color-text);
}

:deep(.p-toggleswitch.p-toggleswitch-checked .p-toggleswitch-slider) {
  background: linear-gradient(90deg, var(--color-success), #33E0A5);
}
</style>
