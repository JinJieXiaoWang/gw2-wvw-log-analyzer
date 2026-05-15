<template>
  <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-6 shadow-lg">
    <!-- 头部 -->
    <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-5">
      <div class="flex items-center gap-4">
        <div
          class="w-12 h-12 rounded-lg flex items-center justify-center text-xl text-white shadow-lg shrink-0"
          :style="{ background: `linear-gradient(135deg, ${roleColors[activeRole]}, ${roleGradients[activeRole]})`, boxShadow: `0 8px 24px -8px ${roleColors[activeRole]}` }"
        >
          <i :class="activeRoleIcon" />
        </div>
        <div>
          <h3 class="text-xl font-semibold text-color">
            {{ activeRoleLabel }}评分规则
            <span
              v-if="ruleScope === 'profession' && selectedProfession"
              class="text-sm font-normal text-color-secondary ml-2"
            >— {{ selectedProfession }}</span>
          </h3>
          <div class="flex items-center gap-3 mt-1 flex-wrap">
            <span class="text-sm text-color-secondary">权重总和</span>
            <div
              class="flex items-baseline gap-1 px-3 py-0.5 rounded-full text-sm font-bold transition-colors"
              :class="weightStatusClass === 'optimal' ? 'bg-green-500/10 text-green-500' : weightStatusClass === 'warning' ? 'bg-orange-500/10 text-orange-500' : 'bg-red-500/10 text-red-500'"
            >
              <span class="text-base">{{ totalWeight.toFixed(2) }}</span>
              <span class="text-xs font-normal opacity-60">/ 1.00</span>
            </div>
            <span
              v-if="weightStatusClass !== 'optimal'"
              class="flex items-center gap-1 text-xs text-orange-500"
            >
              <i class="pi pi-exclamation-circle" />
              建议调整为 1.0
            </span>
          </div>
        </div>
      </div>
      <div
        v-if="canWrite"
        class="flex flex-wrap gap-2"
      >
        <BaseButton
          v-if="ruleScope === 'generic'"
          label="应用到历史数据"
          icon="pi pi-history"
          variant="info"
          outlined
          :loading="recalculating"
          :disabled="!canRecalculate"
          @click="emit('recalculate')"
        />
        <BaseButton
          v-if="ruleScope === 'profession'"
          label="删除职业规则"
          icon="pi pi-trash"
          variant="danger"
          outlined
          :loading="deletingProfession"
          :disabled="!currentProfessionHasRules"
          @click="emit('deleteProfession')"
        />
        <BaseButton
          label="重置默认"
          icon="pi pi-refresh"
          variant="secondary"
          outlined
          :loading="resetting"
          @click="emit('reset')"
        />
        <BaseButton
          label="保存更改"
          icon="pi pi-save"
          :loading="saving"
          :disabled="!hasUnsavedChanges"
          @click="emit('save')"
        />
      </div>
    </div>

    <!-- 权重可视化条 -->
    <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full mb-5 overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="weightStatusClass === 'optimal' ? 'bg-green-500' : weightStatusClass === 'warning' ? 'bg-orange-500' : 'bg-red-500'"
        :style="{ width: `${Math.min(totalWeight * 100, 100)}%` }"
      />
      <div
        class="absolute top-0 bottom-0 w-0.5 bg-white/50"
        style="left: 100%"
      />
    </div>

    <ScoringRulesTable
      :editable-rules="editableRules"
      :loading="loading"
      :can-write="canWrite"
      :get-dimension-icon="getDimensionIcon"
      :get-dimension-color="getDimensionColor"
      :get-dimension-label="getDimensionLabel"
      @move-up="emit('moveUp', $event)"
      @move-down="emit('moveDown', $event)"
      @remove="emit('remove', $event)"
      @mark-changed="emit('markChanged')"
    />

    <AddRuleForm
      :available-dimensions="availableDimensions"
      :can-write="canWrite"
      :get-dimension-icon="getDimensionIcon"
      :get-dimension-color="getDimensionColor"
      :get-dimension-label="getDimensionLabel"
      :active-role="activeRole"
      @add="(d, w, desc) => emit('add', d, w, desc)"
    />
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import ScoringRulesTable from './ScoringRulesTable.vue'
import AddRuleForm from './AddRuleForm.vue'
import type { ScoringRule, DimensionInfo } from '@/services/core/scoringRulesService'

defineProps<{
  activeRole: string
  activeRoleLabel: string
  activeRoleIcon: string
  roleColors: Record<string, string>
  roleGradients: Record<string, string>
  ruleScope: string
  selectedProfession: string
  editableRules: ScoringRule[]
  loading: boolean
  saving: boolean
  resetting: boolean
  recalculating: boolean
  canRecalculate: boolean
  currentProfessionHasRules: boolean
  deletingProfession: boolean
  totalWeight: number
  weightStatusClass: string
  hasUnsavedChanges: boolean
  canWrite: boolean
  newRuleDimension: string
  newRuleWeight: number
  newRuleDesc: string
  availableDimensions: DimensionInfo[]
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
}>()

const emit = defineEmits<{
  save: []
  reset: []
  recalculate: []
  deleteProfession: []
  add: [dimension: string, weight: number, desc: string]
  remove: [index: number]
  moveUp: [index: number]
  moveDown: [index: number]
  markChanged: []
}>()
</script>
