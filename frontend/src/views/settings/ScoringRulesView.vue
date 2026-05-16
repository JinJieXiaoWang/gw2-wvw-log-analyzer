<template>
  <div class="relative min-h-screen bg-neutral-bg p-4 sm:p-6 overflow-hidden">
    <!-- 背景装饰 -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div class="deco-circle deco-circle-top" />
      <div class="deco-circle deco-circle-bottom" />
      <div class="deco-grid" />
    </div>

    <div class="relative z-10 max-w-[1400px] mx-auto flex flex-col gap-4 sm:gap-6">
      <PageHeader
        :title="PAGE_TITLE"
        :subtitle="PAGE_SUBTITLE"
        icon="pi pi-sliders-h"
        icon-gradient="bg-gradient-to-br from-primary via-ai to-secondary"
      />

      <Message
        severity="info"
        class="shadow-sm"
      >
        <div class="flex items-start gap-3">
          <i class="pi pi-calculator mt-0.5 text-info-500" />
          <div class="text-sm leading-relaxed">
            <strong>{{ AUTO_CALCULATION.TITLE }}</strong>{{ AUTO_CALCULATION.DESCRIPTION_PREFIX }}<strong>{{ AUTO_CALCULATION.HIGHLIGHT }}</strong>{{ AUTO_CALCULATION.DESCRIPTION_SUFFIX }}
          </div>
        </div>
      </Message>

      <!-- 角色类型卡片 -->
      <ScoringRoleCards
        :roles="roleTypes"
        :active-role="activeRole"
        :colors="roleColors"
        :gradients="roleGradients"
        :rule-counts="ruleCounts"
        :unsaved-roles="changedRoles"
        :progress="weightProgress"
        @switch="switchRole"
      />

      <!-- 规则范围 -->
      <RuleScopeSelector
        v-model:selected-profession="selectedProfession"
        v-model:selected-base-profession="selectedBaseProfession"
        :scope="ruleScope"
        :cascade-professions="cascadeProfessions"
        @change-scope="switchScope"
        @base-profession-change="onBaseProfessionChange"
        @profession-change="onProfessionChange"
      />

      <!-- 规则编辑器 -->
      <ScoringRulesEditor
        :active-role="activeRole"
        :active-role-label="activeRoleLabel"
        :active-role-icon="activeRoleIcon"
        :role-colors="roleColors"
        :role-gradients="roleGradients"
        :rule-scope="ruleScope"
        :selected-profession="selectedProfession"
        :editable-rules="editableRules"
        :loading="loading"
        :saving="saving"
        :resetting="resetting"
        :recalculating="recalculating"
        :can-recalculate="canRecalculate"
        :current-profession-has-rules="currentProfessionHasRules"
        :deleting-profession="deletingProfession"
        :total-weight="totalWeight"
        :weight-status-class="weightStatusClass"
        :has-unsaved-changes="hasUnsavedChanges(activeRole)"
        :can-write="canWrite"
        :new-rule-dimension="newRuleDimension"
        :new-rule-weight="newRuleWeight"
        :new-rule-desc="newRuleDesc"
        :available-dimensions="availableDimensions"
        :get-dimension-icon="getDimensionIcon"
        :get-dimension-color="getDimensionColor"
        :get-dimension-label="getDimensionLabel"
        @recalculate="confirmRecalculate"
        @delete-profession="confirmDeleteProfessionRules"
        @reset="confirmReset"
        @save="saveChanges"
        @move-up="moveUp"
        @move-down="moveDown"
        @mark-changed="markChanged"
        @remove="removeRule"
        @add="addRule"
      />

      <!-- 职业定位管理 -->
      <ProfessionRoleEditor
        :role-types="roleTypes"
        :profession-role-mapping="professionRoleMapping"
        :is-edit-mode="roleEditMode"
        :can-write="canWrite"
        :scoring-mode="scoringMode"
        @toggle-edit="toggleRoleEditMode"
        @save="saveRoleMapping"
        @profession-change="updateProfessionRole"
      />

      <!-- 评分等级 -->
      <ScoringGradeCards :grades="gradeList" />

      <!-- 重算任务 -->
      <RecalcTaskPanel
        :task="recalcTask"
        :severity="recalcStatusSeverity"
        @close="recalcTask = null"
      />

      <!-- 版本历史 -->
      <VersionHistoryTable
        :versions="versionHistory"
        :format-date="formatDate"
      />
    </div>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/layout/components/PageHeader.vue'
import Message from 'primevue/message'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import RuleScopeSelector from '@/components/settings/scoring/RuleScopeSelector.vue'
import ProfessionRoleEditor from '@/components/settings/scoring/ProfessionRoleEditor.vue'
import ScoringRulesEditor from '@/components/settings/scoring/ScoringRulesEditor.vue'
import ScoringRoleCards from '@/components/settings/scoring/ScoringRoleCards.vue'
import ScoringGradeCards from '@/components/settings/scoring/ScoringGradeCards.vue'
import RecalcTaskPanel from '@/components/settings/scoring/RecalcTaskPanel.vue'
import VersionHistoryTable from '@/components/settings/scoring/VersionHistoryTable.vue'
import { ref, computed, onMounted } from 'vue'
import { useScoringRules } from '@/composables/scoring/useScoringRules'
import { usePermission } from '@/composables/system/usePermission'
import { professionService } from '@/services'

// === 常量定义 ===
const PAGE_TITLE = '评分规则配置'
const PAGE_SUBTITLE = '为不同角色类型定制评分维度和权重'
const AUTO_CALCULATION = {
  TITLE: '评分自动计算机制：',
  DESCRIPTION_PREFIX: '当日志导入完成后，系统会根据当前生效的评分规则版本，结合玩家的职业和角色定位，',
  HIGHLIGHT: '自动计算',
  DESCRIPTION_SUFFIX: '每个玩家的 AI 评分与等级。修改规则后，可通过"应用到历史数据"按钮重新计算历史日志。',
} as const
const ROLE_FALLBACK = 'dps'
const LOG_LOAD_ROLE_MAPPING_FAIL = '加载职业角色映射失败:'

const { can } = usePermission()
const canWrite = can('write')

const {
  roleTypes, activeRole, loading, saving, resetting, currentRules, editableRules,
  changedRoles, allDimensions, newRuleDimension, newRuleWeight, newRuleDesc,
  ruleScope, selectedProfession, professionOptions, professionRulesMap,
  deletingProfession, cascadeProfessions, selectedBaseProfession,
  recalculating, recalcTask, versionHistory,
  roleColors, roleGradients, activeRoleLabel, activeRoleIcon,
  canRecalculate, currentProfessionHasRules, recalcStatusSeverity,
  totalWeight, availableDimensions, weightStatusClass, gradeList,
  hasUnsavedChanges, getWeightProgress, getDimensionIcon, getDimensionColor, getDimensionLabel,
  switchRole, markChanged, moveUp, moveDown, removeRule, addRule,
  saveChanges, confirmReset, switchScope, onBaseProfessionChange, onProfessionChange,
  fetchProfessions, fetchVersions, confirmRecalculate, confirmDeleteProfessionRules,
  formatDate,
} = useScoringRules()

const ruleCounts = computed(() => {
  const map: Record<string, number> = {}
  for (const key of Object.keys(currentRules.value)) {
    map[key] = currentRules.value[key]?.length || 0
  }
  return map
})

const weightProgress = computed(() => {
  const map: Record<string, number> = {}
  for (const role of roleTypes.value) {
    map[role.type] = getWeightProgress(role.type)
  }
  return map
})

// 职业定位管理
const scoringMode = ref<'role_based' | 'profession_based'>('role_based')
const roleEditMode = ref(false)
const professionRoleMapping = ref<any[]>([])
const isLoadingRoleMapping = ref(false)

async function loadProfessionRoleMapping() {
  isLoadingRoleMapping.value = true
  try {
    const professions = await professionService.getProfessions(false)
    professionRoleMapping.value = professions.map(p => ({
      profession: p.profession_name,
      professionKey: p.profession_key,
      role: p.elite_specializations?.[0]?.role_type || ROLE_FALLBACK,
      roleLabel: p.elite_specializations?.[0]?.role_type || ROLE_FALLBACK,
      icon: 'pi pi-user',
      eliteSpecs: (p.elite_specializations || []).map((s: any) => s.spec_name),
      currentRole: p.elite_specializations?.[0]?.role_type || ROLE_FALLBACK
    }))
  } catch (error) {
    console.error(LOG_LOAD_ROLE_MAPPING_FAIL, error)
  } finally {
    isLoadingRoleMapping.value = false
  }
}

function toggleRoleEditMode() {
  roleEditMode.value = !roleEditMode.value
  if (roleEditMode.value) {
    professionRoleMapping.value.forEach(p => { p.currentRole = p.role })
  }
}

function updateProfessionRole(prof: any) {
  const item = professionRoleMapping.value.find(p => p.profession === prof.profession)
  if (item) {
    item.currentRole = prof.currentRole
  }
}

function saveRoleMapping() {
  professionRoleMapping.value.forEach(p => { p.role = p.currentRole })
  roleEditMode.value = false
  // TODO: 调用 API 保存角色映射
}

onMounted(() => {
  loadProfessionRoleMapping()
})
</script>

<style scoped>
.deco-circle {
  @apply absolute rounded-full blur-[80px] opacity-15 animate-pulse;
}

.deco-circle-top {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-ai));
  top: -200px;
  right: -100px;
}

.deco-circle-bottom {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, var(--color-secondary), var(--color-error));
  bottom: -100px;
  left: -100px;
  animation-delay: 1s;
}

.deco-grid {
  @apply absolute inset-0;
  background-image: linear-gradient(color-mix(in srgb, var(--color-primary) 3%, transparent) 1px, transparent 1px), linear-gradient(90deg, color-mix(in srgb, var(--color-primary) 3%, transparent) 1px, transparent 1px);
  background-size: 50px 50px;
}
</style>
