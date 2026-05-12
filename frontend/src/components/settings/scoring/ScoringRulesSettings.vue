<template>
  <div class="card">
    <!-- 头部 -->
    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
      <div
        class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/10 flex
               items-center justify-center border border-primary/20">
        <i class="pi pi-chart-line text-primary text-xl" />
      </div>
      <div>
        <h3 class="text-lg font-bold text-neutral-text">
          评分规则配置
        </h3>
        <p class="text-sm text-neutral-text-secondary mt-0.5">
          为不同角色类型定制评分维度和权重
        </p>
      </div>
    </div>

    <!-- 角色类型选择 -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <button
        v-for="role in roleTypes"
        :key="role.type"
        class="relative p-4 rounded-xl border-2 transition-all duration-200 text-left"
        :class="activeRole === role.type ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10' : 'border-neutral-border bg-neutral-bg-secondary hover:border-neutral-border-dark'"
        @click="switchRole(role.type)"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-base"
            :class="roleIconBgClass(role.type)"
          >
            <i :class="role.icon" />
          </div>
          <div>
            <h4 class="font-semibold text-neutral-text text-sm">
              {{ role.label }}
            </h4>
            <p class="text-xs text-neutral-text-secondary">
              {{ role.description }}
            </p>
          </div>
        </div>
        <div
          v-if="hasUnsavedChanges(role.type)"
          class="absolute top-2 right-2"
        >
          <span
            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                   bg-warning/20 text-warning">已修改</span>
        </div>
      </button>
    </div>

    <!-- 规则表格 -->
    <ScoringRulesTable
      :editable-rules="editableRules"
      :loading="loading"
      :total-weight="totalWeight"
      :available-dimensions="availableDimensions"
      :new-dimension="newRuleDimension"
      :new-weight="newRuleWeight"
      :new-desc="newRuleDesc"
      :has-changes="hasUnsavedChanges(activeRole)"
      :get-dimension-icon="getDimensionIcon"
      :get-dimension-color="getDimensionColor"
      :get-dimension-label="getDimensionLabel"
      @move-up="moveUp"
      @move-down="moveDown"
      @mark-changed="markChanged"
      @remove="removeRule"
      @add="addRule"
      @reset="confirmReset"
      @cancel="resetChanges"
      @save="saveChanges"
    />

    <!-- 评分等级说明 -->
    <ScoringGradeCards :grades="gradeList" />

    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import ConfirmDialog from 'primevue/confirmdialog'
import ScoringRulesTable from './ScoringRulesTable.vue'
import ScoringGradeCards from './ScoringGradeCards.vue'
import { useScoringRules } from '@/composables/scoring/useScoringRules'

const confirm = useConfirm()
const toast = useToast()

const {
  roleTypes, activeRole, loading, editableRules,
  changedRoles, allDimensions, newRuleDimension, newRuleWeight, newRuleDesc,
  totalWeight, availableDimensions, gradeList,
  hasUnsavedChanges, getDimensionIcon, getDimensionColor, getDimensionLabel,
  fetchRules, fetchDimensions, syncEditableRules,
  switchRole, markChanged, moveUp, moveDown, removeRule, addRule,
  saveChanges, resetChanges, confirmReset,
} = useScoringRules()

function roleIconBgClass(role: string) {
  const map: Record<string, string> = {
    dps: 'bg-gradient-to-br from-error to-orange-500',
    support: 'bg-gradient-to-br from-success to-info',
    tank: 'bg-gradient-to-br from-purple-500 to-primary',
  }
  return map[role] || 'bg-gradient-to-br from-primary to-secondary'
}

onMounted(() => {
  fetchRules()
  fetchDimensions()
})

watch(activeRole, () => syncEditableRules())
</script>


