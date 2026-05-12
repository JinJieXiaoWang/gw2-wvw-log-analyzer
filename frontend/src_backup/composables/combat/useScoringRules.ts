/**
 * useScoringRules - 评分规则配置业务逻辑 composable
 * 功能：管理评分规则页面的所有状态、计算属性、数据请求
 */

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { scoringRulesService, type ScoringRule, type DimensionInfo } from '@/services/core/scoringRulesService'
import { dictionaryService, type ProfessionCascade } from '@/services/system/dictionaryService'
import { configManager } from '@/services/core/configManager'
import { ROLE_ICON_MAP, ROLE_GRADIENT_MAP, DEFAULT_ROLE_TYPES, DIMENSION_ICONS, DIMENSION_COLORS } from '@/utils/combat/scoringConstants'

export function useScoringRules() {
  const confirm = useConfirm()
  const toast = useToast()

  // ========== State ==========
  const loading = ref(false)
  const saving = ref(false)
  const resetting = ref(false)
  const deletingProfession = ref(false)
  const recalculating = ref(false)

  const roleTypes = ref<{ type: string; label: string; description: string; icon: string; color: string }[]>([])
  const activeRole = ref('')
  const currentRules = ref<Record<string, ScoringRule[]>>({})
  const editableRules = ref<ScoringRule[]>([])
  const changedRoles = ref<Set<string>>(new Set())
  const allDimensions = ref<DimensionInfo[]>([])

  const newRuleDimension = ref('')
  const newRuleWeight = ref(10)
  const newRuleDesc = ref('')

  const ruleScope = ref<'generic' | 'profession'>('generic')
  const selectedProfession = ref('')
  const professionOptions = ref<{ label: string; value: string }[]>([])
  const professionRulesMap = ref<Record<string, ScoringRule[]>>({})
  const cascadeProfessions = ref<ProfessionCascade[]>([])
  const selectedBaseProfession = ref('')

  const recalcTask = ref<any>(null)
  let recalcPollTimer: ReturnType<typeof setInterval> | null = null

  const versionHistory = ref<any[]>([])

  // ========== Computed ==========
  const roleColors = computed(() => {
    const map: Record<string, string> = {}
    for (const r of roleTypes.value) map[r.type] = r.color || '#6b7280'
    return map
  })

  const roleGradients = computed(() => {
    const map: Record<string, string> = {}
    for (const r of roleTypes.value) map[r.type] = ROLE_GRADIENT_MAP[r.type] || r.color || '#6b7280'
    return map
  })

  const activeRoleLabel = computed(() => roleTypes.value.find(r => r.type === activeRole.value)?.label || '')
  const activeRoleIcon = computed(() => roleTypes.value.find(r => r.type === activeRole.value)?.icon || 'pi pi-star')

  const canRecalculate = computed(() => ruleScope.value === 'generic' && !recalculating.value && !hasUnsavedChanges(activeRole.value))

  const currentProfessionHasRules = computed(() => selectedProfession.value && (professionRulesMap.value[selectedProfession.value]?.length || 0) > 0)

  const recalcStatusSeverity = computed(() => {
    const s = recalcTask.value?.status
    if (s === 'completed') return 'success'
    if (s === 'processing') return 'warning'
    if (s === 'failed') return 'danger'
    return 'info'
  })

  const totalWeight = computed(() => editableRules.value.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0))

  const availableDimensions = computed(() => {
    const used = new Set(editableRules.value.map(r => r.dimension))
    return allDimensions.value.filter(d => !used.has(d.key))
  })

  const weightStatusClass = computed(() => {
    const diff = Math.abs(totalWeight.value - 1.0)
    if (diff < 0.01) return 'optimal'
    if (diff < 0.1) return 'warning'
    return 'error'
  })

  const filteredEliteSpecs = computed(() => {
    const prof = cascadeProfessions.value.find(p => p.value === selectedBaseProfession.value)
    return prof?.elite_specs || []
  })

  // ========== Helpers ==========
  function hasUnsavedChanges(role: string) {
    return changedRoles.value.has(role)
  }

  function getWeightProgress(role: string): number {
    const rules = currentRules.value[role] || []
    const total = rules.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
    return Math.min(total * 100, 100)
  }

  function getProfessionColor(value: string): string {
    return cascadeProfessions.value.find(p => p.value === value)?.color || '#6b7280'
  }

  function getProfessionLabel(value: string): string {
    return cascadeProfessions.value.find(p => p.value === value)?.label || value
  }

  function getSpecColor(value: string): string {
    for (const prof of cascadeProfessions.value) {
      const spec = prof.elite_specs.find(s => s.value === value)
      if (spec) return spec.color
    }
    return '#6b7280'
  }

  function getSpecLabel(value: string): string {
    for (const prof of cascadeProfessions.value) {
      const spec = prof.elite_specs.find(s => s.value === value)
      if (spec) return spec.label
    }
    return value
  }

  function getDimensionIcon(key: string): string {
    return DIMENSION_ICONS[key] || 'pi pi-circle'
  }

  function getDimensionColor(key: string): string {
    return DIMENSION_COLORS[key] || '#888888'
  }

  function getDimensionLabel(key: string) {
    return allDimensions.value.find(d => d.key === key)?.label || key
  }

  function formatDate(dateStr?: string): string {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  // ========== Data Fetching ==========
  async function fetchRoleTypes() {
    try {
      const data = await scoringRulesService.getRoleTypes()
      if (data && data.length > 0) {
        roleTypes.value = data.map((r: any) => ({
          type: r.type, label: r.label, description: r.description || '',
          icon: ROLE_ICON_MAP[r.type] || 'pi pi-star', color: r.color || '#6b7280',
        }))
        if (!activeRole.value) activeRole.value = data[0].type
      }
    } catch {
      roleTypes.value = DEFAULT_ROLE_TYPES.map(r => ({ ...r }))
      activeRole.value = 'dps'
    }
  }

  async function fetchRules() {
    loading.value = true
    try {
      if (ruleScope.value === 'profession' && selectedProfession.value) {
        const data = await scoringRulesService.getRules(activeRole.value, selectedProfession.value)
        if (data?.rules) professionRulesMap.value[selectedProfession.value] = data.rules
      } else {
        const data = await scoringRulesService.getRules()
        if (data) {
          for (const key of ['dps', 'support', 'tank']) {
            if (data[key]) currentRules.value[key] = data[key].rules || []
          }
        }
      }
      syncEditableRules()
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分规则失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      loading.value = false
    }
  }

  async function fetchDimensions() {
    try { allDimensions.value = await scoringRulesService.getDimensions() }
    catch (e) { console.error('获取评分维度失败', e) }
  }

  async function fetchProfessions() {
    try {
      const data = await dictionaryService.getProfessionSpecsCascade()
      if (data?.professions) {
        cascadeProfessions.value = data.professions
        professionOptions.value = []
        for (const prof of data.professions) {
          for (const spec of prof.elite_specs) {
            professionOptions.value.push({ label: `${spec.label} (${prof.label})`, value: spec.value })
          }
        }
      }
    } catch {
      toast.add({ severity: 'warn', summary: '提示', detail: '获取职业列表失败，请刷新字典缓存', life: configManager.get('ui').toastLife })
    }
  }

  async function fetchVersions() {
    try { versionHistory.value = await scoringRulesService.getVersions(0, 10) }
    catch (e) { console.error('获取版本历史失败', e) }
  }

  function syncEditableRules() {
    let rules: ScoringRule[] = []
    if (ruleScope.value === 'profession' && selectedProfession.value) {
      rules = professionRulesMap.value[selectedProfession.value] || []
    } else {
      rules = currentRules.value[activeRole.value] || []
    }
    editableRules.value = rules.map(r => ({ ...r }))
  }

  // ========== Actions ==========
  function switchRole(role: string) {
    activeRole.value = role
    syncEditableRules()
  }

  function switchScope(scope: 'generic' | 'profession') {
    ruleScope.value = scope
    if (scope === 'profession' && cascadeProfessions.value.length === 0) fetchProfessions()
    syncEditableRules()
  }

  function markChanged() { changedRoles.value.add(activeRole.value) }

  function moveUp(index: number) {
    if (index === 0) return
    const temp = editableRules.value[index]
    editableRules.value[index] = editableRules.value[index - 1]
    editableRules.value[index - 1] = temp
    markChanged()
  }

  function moveDown(index: number) {
    if (index >= editableRules.value.length - 1) return
    const temp = editableRules.value[index]
    editableRules.value[index] = editableRules.value[index + 1]
    editableRules.value[index + 1] = temp
    markChanged()
  }

  function removeRule(index: number) {
    editableRules.value.splice(index, 1)
    markChanged()
  }

  function addRule() {
    if (!newRuleDimension.value) return
    const dim = allDimensions.value.find(d => d.key === newRuleDimension.value)
    editableRules.value.push({
      id: 0, role_type: activeRole.value, dimension: newRuleDimension.value,
      weight: newRuleWeight.value / 100, is_active: true,
      description: newRuleDesc.value || dim?.label || '', sort_order: editableRules.value.length,
    })
    newRuleDimension.value = ''
    newRuleWeight.value = 10
    newRuleDesc.value = ''
    markChanged()
  }

  async function saveChanges() {
    saving.value = true
    try {
      const rulesToSave = editableRules.value.map((r, idx) => ({
        role_type: activeRole.value, dimension: r.dimension, weight: r.weight,
        is_active: r.is_active, description: r.description, sort_order: idx,
        min_value: r.min_value, max_value: r.max_value,
      }))
      if (ruleScope.value === 'profession' && selectedProfession.value) {
        await scoringRulesService.upsertProfessionRules(selectedProfession.value, activeRole.value, rulesToSave)
        const refreshed = await scoringRulesService.getRules(activeRole.value, selectedProfession.value)
        if (refreshed?.rules) professionRulesMap.value[selectedProfession.value] = refreshed.rules
        toast.add({ severity: 'success', summary: '保存成功', detail: `${selectedProfession.value} 职业特定规则已更新`, life: configManager.get('ui').toastLife })
      } else {
        await scoringRulesService.batchUpdate(activeRole.value, rulesToSave)
        const refreshed = await scoringRulesService.getRules(activeRole.value)
        if (refreshed?.rules) currentRules.value[activeRole.value] = refreshed.rules
        toast.add({ severity: 'success', summary: '保存成功', detail: `${activeRoleLabel.value}通用评分规则已更新`, life: configManager.get('ui').toastLife })
      }
      changedRoles.value.delete(activeRole.value)
      syncEditableRules()
      await fetchVersions()
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '保存失败', detail: e?.message || '更新评分规则失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      saving.value = false
    }
  }

  function confirmReset() {
    confirm.require({
      message: `确定要将 ${activeRoleLabel.value} 的评分规则重置为系统默认吗？此操作不可撤销。`,
      header: '确认重置', icon: 'pi pi-exclamation-triangle', acceptClass: 'p-button-danger',
      accept: async () => {
        resetting.value = true
        try {
          await scoringRulesService.resetDefault(activeRole.value)
          changedRoles.value.delete(activeRole.value)
          await fetchRules()
          toast.add({ severity: 'success', summary: '重置成功', detail: `${activeRoleLabel.value}评分规则已重置为默认`, life: configManager.get('ui').toastLife })
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '重置失败', detail: e?.message || '操作失败', life: configManager.get('ui').toastErrorLife })
        } finally { resetting.value = false }
      },
    })
  }

  function onBaseProfessionChange() {
    selectedProfession.value = ''
    editableRules.value = []
  }

  function onProfessionChange() {
    if (selectedProfession.value) fetchRules()
    else editableRules.value = []
  }

  // ========== Recalculation ==========
  function confirmRecalculate() {
    confirm.require({
      message: '确定要将当前规则应用到所有历史数据吗？此操作将在后台异步执行，可能需要一段时间。',
      header: '确认应用到历史数据', icon: 'pi pi-history',
      accept: async () => { await startRecalculation() },
    })
  }

  async function startRecalculation() {
    recalculating.value = true
    try {
      const result = await scoringRulesService.triggerRecalculation({}, `${activeRoleLabel.value}通用规则更新后的历史数据重算`)
      if (result) {
        recalcTask.value = { version_id: result.version_id, version: result.version, status: result.status, total_records: 0, updated_records: 0, progress_percent: 0 }
        toast.add({ severity: 'info', summary: '重算任务已创建', detail: `版本 v${result.version}，正在后台执行`, life: configManager.get('ui').toastErrorLife })
        pollRecalcStatus(result.version_id)
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '重算任务创建失败', detail: e?.message || '操作失败', life: configManager.get('ui').toastErrorLife })
    } finally { recalculating.value = false }
  }

  function pollRecalcStatus(versionId: number) {
    if (recalcPollTimer) { clearInterval(recalcPollTimer); recalcPollTimer = null }
    recalcPollTimer = setInterval(async () => {
      try {
        const status = await scoringRulesService.getRecalculationStatus(versionId)
        if (status) {
          recalcTask.value = status
          if (status.status === 'completed' || status.status === 'failed') {
            if (recalcPollTimer) { clearInterval(recalcPollTimer); recalcPollTimer = null }
            if (status.status === 'completed') toast.add({ severity: 'success', summary: '重算完成', detail: `已更新 ${status.updated_records} 条记录`, life: configManager.get('ui').toastErrorLife })
            await fetchVersions()
          }
        }
      } catch (e) { console.error('轮询重算状态失败', e) }
    }, 3000)
  }

  function confirmDeleteProfessionRules() {
    confirm.require({
      message: `确定要删除 ${selectedProfession.value} 的职业特定规则吗？删除后将回退到通用规则。`,
      header: '确认删除职业规则', icon: 'pi pi-exclamation-triangle', acceptClass: 'p-button-danger',
      accept: async () => {
        deletingProfession.value = true
        try {
          await scoringRulesService.deleteProfessionRules(selectedProfession.value)
          professionRulesMap.value[selectedProfession.value] = []
          syncEditableRules()
          toast.add({ severity: 'success', summary: '删除成功', detail: `${selectedProfession.value} 职业特定规则已删除`, life: configManager.get('ui').toastLife })
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '删除失败', detail: e?.message || '操作失败', life: configManager.get('ui').toastErrorLife })
        } finally { deletingProfession.value = false }
      },
    })
  }

  // ========== Lifecycle ==========
  onMounted(async () => {
    await fetchRoleTypes()
    await fetchRules()
    await fetchDimensions()
    await fetchVersions()
  })

  watch(activeRole, syncEditableRules)
  watch(ruleScope, syncEditableRules)

  onUnmounted(() => {
    if (recalcPollTimer) { clearInterval(recalcPollTimer); recalcPollTimer = null }
  })

  // ========== Return ==========
  return {
    // State
    loading, saving, resetting, deletingProfession, recalculating,
    roleTypes, activeRole, currentRules, editableRules, changedRoles,
    allDimensions, newRuleDimension, newRuleWeight, newRuleDesc,
    ruleScope, selectedProfession, professionOptions, professionRulesMap,
    cascadeProfessions, selectedBaseProfession, recalcTask, versionHistory,
    // Computed
    roleColors, roleGradients, activeRoleLabel, activeRoleIcon,
    canRecalculate, currentProfessionHasRules, recalcStatusSeverity,
    totalWeight, availableDimensions, weightStatusClass, filteredEliteSpecs,
    // Helpers
    hasUnsavedChanges, getWeightProgress, getProfessionColor, getProfessionLabel,
    getSpecColor, getSpecLabel, getDimensionIcon, getDimensionColor, getDimensionLabel, formatDate,
    // Actions
    switchRole, switchScope, markChanged, moveUp, moveDown, removeRule, addRule,
    saveChanges, confirmReset, onBaseProfessionChange, onProfessionChange,
    confirmRecalculate, confirmDeleteProfessionRules,
  }
}
