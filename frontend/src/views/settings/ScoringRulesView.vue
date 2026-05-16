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

      <!-- 评分模式概览 -->
      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center shrink-0">
          <i class="pi pi-calculator text-primary-500" />
        </div>
        <div class="min-w-0">
          <div class="text-sm font-medium text-color">当前评分模式：{{ scoringModeLabel }}</div>
          <div class="text-xs text-color-secondary mt-0.5">{{ scoringModeDesc }}</div>
        </div>
      </div>

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

      <!-- 当前角色下的精英特长 -->
      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4">
        <div class="flex items-center gap-2 text-sm text-color-secondary mb-3">
          <i class="pi pi-users" />
          <span>{{ activeRoleLabel }}定位下的精英特长</span>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="spec in currentRoleSpecs"
            :key="spec.professionKey"
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium"
            :style="{ background: roleColors[activeRole] + '18', color: roleColors[activeRole] }"
          >
            {{ spec.profession }}
          </span>
          <span v-if="currentRoleSpecs.length === 0" class="text-xs text-color-secondary">暂无对应精英特长</span>
        </div>
      </div>

      <!-- 规则编辑器 -->
      <ScoringRulesEditor
        v-bind="editorData"
        :has-unsaved-changes="hasUnsavedChanges(activeRole)"
        :get-dimension-icon="getDimensionIcon"
        :get-dimension-color="getDimensionColor"
        :get-dimension-label="getDimensionLabel"
        @recalculate="confirmRecalculate"
        @reset="confirmReset"
        @save="saveChanges"
        @move-up="moveUp"
        @move-down="moveDown"
        @mark-changed="markChanged"
        @remove="removeRule"
        @add="addRule"
      />

      <!-- 高级设置（默认折叠） -->
      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl overflow-hidden">
        <button class="w-full flex items-center justify-between p-4 text-sm font-medium text-color hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors" @click="showAdvanced = !showAdvanced">
          <span class="flex items-center gap-2"><i class="pi pi-cog text-color-secondary" />高级设置（职业定位 / 评分等级 / 历史重算 / 版本）</span>
          <i :class="showAdvanced ? 'pi-chevron-up' : 'pi-chevron-down'" class="pi text-color-secondary" />
        </button>
        <div v-show="showAdvanced" class="p-4 border-t border-surface-200 dark:border-surface-700 flex flex-col gap-4">
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
          <ScoringGradeCards :grades="gradeList" />
          <RecalcTaskPanel :task="recalcTask" :severity="recalcStatusSeverity" @close="recalcTask = null" />
          <VersionHistoryTable :versions="versionHistory" :format-date="formatDate" />
        </div>
      </div>
    </div>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import PageHeader from '@/layout/components/PageHeader.vue'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import ProfessionRoleEditor from '@/components/settings/scoring/ProfessionRoleEditor.vue'
import ScoringRulesEditor from '@/components/settings/scoring/ScoringRulesEditor.vue'
import ScoringRoleCards from '@/components/settings/scoring/ScoringRoleCards.vue'
import ScoringGradeCards from '@/components/settings/scoring/ScoringGradeCards.vue'
import RecalcTaskPanel from '@/components/settings/scoring/RecalcTaskPanel.vue'
import VersionHistoryTable from '@/components/settings/scoring/VersionHistoryTable.vue'
import { ref, computed, onMounted } from 'vue'
import { useScoringRules } from '@/composables/scoring/useScoringRules'
import { usePermission } from '@/composables/system/usePermission'
import { useSystemConfig } from '@/composables/system/useSystemConfig'
import { professionService } from '@/services'

// === 常量定义 ===
const PAGE_TITLE = '评分规则配置'
const PAGE_SUBTITLE = '定义各角色定位的评分维度和权重'
const ROLE_FALLBACK = 'dps'
const LOG_LOAD_ROLE_MAPPING_FAIL = '加载职业角色映射失败:'

const { can } = usePermission()
const canWrite = can('write')

const {
  roleTypes, activeRole, loading, saving, resetting, currentRules, editableRules,
  changedRoles, allDimensions, newRuleDimension, newRuleWeight, newRuleDesc,
  recalculating, recalcTask, versionHistory,
  roleColors, roleGradients, activeRoleLabel, activeRoleIcon,
  canRecalculate, recalcStatusSeverity,
  totalWeight, availableDimensions, weightStatusClass, gradeList,
  hasUnsavedChanges, getWeightProgress, getDimensionIcon, getDimensionColor, getDimensionLabel,
  switchRole, markChanged, moveUp, moveDown, removeRule, addRule,
  saveChanges, confirmReset,
  fetchVersions, confirmRecalculate,
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

// 当前角色下的精英特长
const currentRoleSpecs = computed(() => {
  return professionRoleMapping.value.filter(p => p.role === activeRole.value)
})

// 规则编辑器数据（打包传递减少 template 行数）
const editorData = computed(() => ({
  activeRole: activeRole.value,
  activeRoleLabel: activeRoleLabel.value,
  activeRoleIcon: activeRoleIcon.value,
  roleColors: roleColors.value,
  roleGradients: roleGradients.value,
  ruleScope: 'generic',
  selectedProfession: '',
  editableRules: editableRules.value,
  loading: loading.value,
  saving: saving.value,
  resetting: resetting.value,
  recalculating: recalculating.value,
  canRecalculate: canRecalculate.value,
  currentProfessionHasRules: false,
  deletingProfession: false,
  totalWeight: totalWeight.value,
  weightStatusClass: weightStatusClass.value,
  canWrite,
  newRuleDimension: newRuleDimension.value,
  newRuleWeight: newRuleWeight.value,
  newRuleDesc: newRuleDesc.value,
  availableDimensions: availableDimensions.value,
}))

// 系统配置
const { getConfig, loadSystemConfigs } = useSystemConfig()

// 评分模式
const scoringMode = ref<'role_based' | 'profession_based'>('role_based')
const scoringModeLabel = computed(() => scoringMode.value === 'role_based' ? '角色定位评分' : '职业评分')
const scoringModeDesc = computed(() =>
  scoringMode.value === 'role_based'
    ? '所有职业按默认定位（输出/辅助/坦克/控制）应用对应的通用评分规则'
    : '优先使用职业特定评分规则，无则回退到角色定位规则'
)

// 高级设置折叠
const showAdvanced = ref(false)

// 职业定位管理
const roleEditMode = ref(false)
const professionRoleMapping = ref<any[]>([])
const isLoadingRoleMapping = ref(false)

async function loadScoringMode() {
  try {
    await loadSystemConfigs()
    scoringMode.value = (getConfig('scoring_mode', 'role_based') as 'role_based' | 'profession_based') || 'role_based'
  } catch (error) {
    console.error('加载评分模式配置失败:', error)
  }
}

async function loadProfessionRoleMapping() {
  isLoadingRoleMapping.value = true
  try {
    const specs = await professionService.getEliteSpecs()
    professionRoleMapping.value = specs.map(s => ({
      profession: s.spec_name,
      professionKey: s.spec_key,
      role: s.role_type || ROLE_FALLBACK,
      roleLabel: s.role_type || ROLE_FALLBACK,
      icon: s.icon || 'pi pi-user',
      eliteSpecs: [],
      currentRole: s.role_type || ROLE_FALLBACK
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
  const item = professionRoleMapping.value.find(p => p.professionKey === prof.professionKey)
  if (item) {
    item.currentRole = prof.currentRole
  }
}

async function saveRoleMapping() {
  const changed = professionRoleMapping.value.filter(p => p.currentRole !== p.role)
  if (changed.length === 0) {
    roleEditMode.value = false
    return
  }
  try {
    await Promise.all(
      changed.map(p => professionService.updateSpecRole(p.professionKey, p.currentRole))
    )
    professionRoleMapping.value.forEach(p => { p.role = p.currentRole })
    roleEditMode.value = false
  } catch (error) {
    console.error('保存职业定位失败:', error)
  }
}

onMounted(() => {
  loadScoringMode()
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
