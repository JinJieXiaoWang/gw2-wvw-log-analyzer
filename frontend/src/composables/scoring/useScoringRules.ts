import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { scoringRulesService, type ScoringRule, type DimensionInfo } from '@/services/core/scoringRulesService'
import { dictionaryService, type ProfessionCascade } from '@/services/system/dictionaryService'
import { professionService } from '@/services/professionService'
const roleIconMap: Record<string, string> = { dps: 'pi pi-bolt', support: 'pi pi-heart', tank: 'pi pi-shield', condition: 'pi pi-fire', healing: 'pi pi-heart-fill', control: 'pi pi-lock', utility: 'pi pi-wrench' }
const roleGradientMap: Record<string, string> = { dps: '#FF8A65', support: '#00B4FF', tank: '#165DFF', condition: '#FF6B35', healing: '#00E5A0', control: '#6366F1', utility: '#0EA5E9' }
export function useScoringRules() {
  const confirm = useConfirm()
  const toast = useToast()
  const roleTypes = ref<{ type: string; label: string; description: string; icon: string; color: string }[]>([])
  const activeRole = ref('')
  const loading = ref(false)
  const saving = ref(false)
  const resetting = ref(false)
  const currentRules = ref<Record<string, ScoringRule[]>>({})
  const originalRules = ref<Record<string, ScoringRule[]>>({})
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
  const deletingProfession = ref(false)
  const cascadeProfessions = ref<ProfessionCascade[]>([])
  const selectedBaseProfession = ref('')
  const recalculating = ref(false)
  const recalcTask = ref<any>(null)
  let recalcPollTimer: ReturnType<typeof setInterval> | null = null
  const versionHistory = ref<any[]>([])
  const roleColors = computed(() => {
    const map: Record<string, string> = {}
    for (const r of roleTypes.value) map[r.type] = r.color || '#6b7280'
    return map
  })
  const roleGradients = computed(() => {
    const map: Record<string, string> = {}
    for (const r of roleTypes.value) map[r.type] = roleGradientMap[r.type] || r.color || '#6b7280'
    return map
  })
  const activeRoleLabel = computed(() => roleTypes.value.find(r => r.type === activeRole.value)?.label || '')
  const activeRoleIcon = computed(() => roleTypes.value.find(r => r.type === activeRole.value)?.icon || 'pi pi-star')
  const canRecalculate = computed(() => ruleScope.value === 'generic' && !recalculating.value && !hasUnsavedChanges(activeRole.value))
  const currentProfessionHasRules = computed(() => !!(selectedProfession.value && (professionRulesMap.value[selectedProfession.value]?.length || 0) > 0))
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
  const gradeList = [
    { grade: 'S', range: '≥90分', desc: '表现卓越，远超平均水平', color: '#FFD700', color2: '#FFA500' },
    { grade: 'A', range: '≥80分', desc: '表现优秀，高于平均水平', color: '#00D68F', color2: '#00B4FF' },
    { grade: 'B', range: '≥70分', desc: '表现良好，达到平均水平', color: '#165DFF', color2: '#4080FF' },
    { grade: 'C', range: '≥60分', desc: '表现一般，略低于平均', color: '#FFAA00', color2: '#FFB347' },
    { grade: 'D', range: '≥40分', desc: '表现较差，需要改进', color: '#FF6B35', color2: '#FF8A65' },
    { grade: 'F', range: '<40分', desc: '表现很差，急需提升', color: '#FF4D6A', color2: '#FF8A80' },
  ]
  function hasUnsavedChanges(role: string): boolean {
    return changedRoles.value.has(role)
  }
  function getWeightProgress(role: string): number {
    const rules = currentRules.value[role] || []
    const total = rules.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
    return Math.min(total * 100, 100)
  }
  const dimensionIcons: Record<string, string> = {
    damage: 'pi pi-bolt', healing: 'pi pi-heart', protection: 'pi pi-shield',
    crowd_control: 'pi pi-lock', support: 'pi pi-star', survival: 'pi pi-users',
    objective: 'pi pi-flag', downstacks: 'pi pi-arrow-down',
  }
  const dimensionColors: Record<string, string> = {
    damage: '#FF4D6A', healing: '#00D68F', protection: '#165DFF',
    crowd_control: '#9D4EDD', support: '#FFAA00', survival: '#00B4FF',
    objective: '#4CAF50', downstacks: '#FF5722',
  }
  function getDimensionIcon(key: string): string { return dimensionIcons[key] || 'pi pi-circle' }
  function getDimensionColor(key: string): string { return dimensionColors[key] || '#888888' }
  function getDimensionLabel(key: string) { return allDimensions.value.find(d => d.key === key)?.label || key }
  async function fetchRules() {
    loading.value = true
    try {
      if (ruleScope.value === 'profession' && selectedProfession.value) {
        const data = await scoringRulesService.getRules(activeRole.value, selectedProfession.value)
        if (data && data.rules) professionRulesMap.value[selectedProfession.value] = data.rules
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
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分规则失败', life: 5000 })
    } finally {
      loading.value = false
    }
  }
  async function fetchDimensions() {
    try { allDimensions.value = await scoringRulesService.getDimensions() } catch (e) { console.error('获取评分维度失败', e) }
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
  function switchRole(role: string) {
    activeRole.value = role
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
        if (refreshed && refreshed.rules) professionRulesMap.value[selectedProfession.value] = refreshed.rules
        toast.add({ severity: 'success', summary: '保存成功', detail: `${selectedProfession.value} 职业特定规则已更新`, life: 3000 })
      } else {
        await scoringRulesService.batchUpdate(activeRole.value, rulesToSave)
        const refreshed = await scoringRulesService.getRules(activeRole.value)
        if (refreshed && refreshed.rules) currentRules.value[activeRole.value] = refreshed.rules
        toast.add({ severity: 'success', summary: '保存成功', detail: `${activeRoleLabel.value}通用评分规则已更新`, life: 3000 })
      }
      changedRoles.value.delete(activeRole.value)
      syncEditableRules()
      await fetchVersions()
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '保存失败', detail: e?.message || '更新评分规则失败', life: 5000 })
    } finally {
      saving.value = false
    }
  }
  function resetChanges() {
    if (!hasUnsavedChanges(activeRole.value)) return
    currentRules.value[activeRole.value] = JSON.parse(JSON.stringify(originalRules.value[activeRole.value] || []))
    changedRoles.value.delete(activeRole.value)
    syncEditableRules()
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
          toast.add({ severity: 'success', summary: '重置成功', detail: `${activeRoleLabel.value}评分规则已重置为默认`, life: 3000 })
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '重置失败', detail: e?.message || '操作失败', life: 5000 })
        } finally {
          resetting.value = false
        }
      },
    })
  }
  function switchScope(scope: 'generic' | 'profession') {
    ruleScope.value = scope
    if (scope === 'profession' && cascadeProfessions.value.length === 0) fetchProfessions()
    syncEditableRules()
  }
  function onBaseProfessionChange() {
    selectedProfession.value = ''
    editableRules.value = []
  }
  function onProfessionChange() {
    if (selectedProfession.value) fetchRules()
    else editableRules.value = []
  }
  async function fetchProfessions() {
    try {
      const cascadeData = await professionService.getProfessionCascade()
      if (cascadeData && cascadeData.length > 0) {
        cascadeProfessions.value = cascadeData.map((prof: any) => ({
          value: prof.value, label: prof.label, color: prof.color,
          default_role: prof.default_role || prof.value,
          elite_specs: (prof.elite_specs || []).map((spec: any) => ({
            value: spec.value, label: spec.label, color: spec.color,
            default_role: spec.default_role || spec.value,
          })),
        }))
        professionOptions.value = []
        for (const prof of cascadeProfessions.value) {
          for (const spec of (prof as any).elite_specs) {
            professionOptions.value.push({ label: `${spec.label} (${prof.label})`, value: spec.value })
          }
        }
      } else {
        const data = await dictionaryService.getProfessionSpecsCascade()
        if (data && data.professions) {
          cascadeProfessions.value = data.professions
          professionOptions.value = []
          for (const prof of data.professions) {
            for (const spec of prof.elite_specs) {
              professionOptions.value.push({ label: `${spec.label} (${prof.label})`, value: spec.value })
            }
          }
        }
      }
    } catch (e) {
      console.error('获取职业级联数据失败', e)
      toast.add({ severity: 'warn', summary: '提示', detail: '获取职业列表失败，请刷新字典缓存', life: 3000 })
    }
  }
  async function fetchVersions() {
    try { versionHistory.value = await scoringRulesService.getVersions(0, 10) } catch (e) { console.error('获取版本历史失败', e) }
  }
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
        toast.add({ severity: 'info', summary: '重算任务已创建', detail: `版本 v${result.version}，正在后台执行`, life: 5000 })
        pollRecalcStatus(result.version_id)
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '重算任务创建失败', detail: e?.message || '操作失败', life: 5000 })
    } finally {
      recalculating.value = false
    }
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
            if (status.status === 'completed') {
              toast.add({ severity: 'success', summary: '重算完成', detail: `已更新 ${status.updated_records} 条记录`, life: 5000 })
            }
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
          toast.add({ severity: 'success', summary: '删除成功', detail: `${selectedProfession.value} 职业特定规则已删除`, life: 3000 })
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '删除失败', detail: e?.message || '操作失败', life: 5000 })
        } finally {
          deletingProfession.value = false
        }
      },
    })
  }
  function formatDate(dateStr?: string): string {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }
  async function fetchRoleTypes() {
    try {
      const data = await scoringRulesService.getRoleTypes()
      if (data && data.length > 0) {
        roleTypes.value = data.map((r: any) => ({
          type: r.type, label: r.label, description: r.description || '',
          icon: roleIconMap[r.type] || 'pi pi-star', color: r.color || '#6b7280',
        }))
        if (!activeRole.value) activeRole.value = data[0].type
      }
    } catch (e) {
      console.error('获取角色类型失败', e)
      roleTypes.value = [
        { type: 'dps', label: '输出', description: '以伤害输出为主要职责', icon: 'pi pi-bolt', color: '#FF4D6A' },
        { type: 'support', label: '辅助', description: '以治疗和增益为主要职责', icon: 'pi pi-heart', color: '#00D68F' },
        { type: 'tank', label: '承伤', description: '以吸收伤害和控制为主要职责', icon: 'pi pi-shield', color: '#9D4EDD' },
      ]
      activeRole.value = 'dps'
    }
  }
  onMounted(async () => {
    await fetchRoleTypes()
    await fetchRules()
    await fetchDimensions()
    await fetchVersions()
  })
  watch(activeRole, () => syncEditableRules())
  watch(ruleScope, () => syncEditableRules())
  onUnmounted(() => { if (recalcPollTimer) clearInterval(recalcPollTimer) })
  return {
    roleTypes, activeRole, loading, saving, resetting, currentRules, originalRules, editableRules,
    changedRoles, allDimensions, newRuleDimension, newRuleWeight, newRuleDesc,
    ruleScope, selectedProfession, professionOptions, professionRulesMap,
    deletingProfession, cascadeProfessions, selectedBaseProfession,
    recalculating, recalcTask, versionHistory,
    roleColors, roleGradients, activeRoleLabel, activeRoleIcon,
    canRecalculate, currentProfessionHasRules, recalcStatusSeverity,
    totalWeight, availableDimensions, weightStatusClass, gradeList,
    hasUnsavedChanges, getWeightProgress, getDimensionIcon, getDimensionColor, getDimensionLabel,
    fetchRules, fetchDimensions, syncEditableRules,
    switchRole, markChanged, moveUp, moveDown, removeRule, addRule,
    saveChanges, resetChanges, confirmReset, switchScope, onBaseProfessionChange, onProfessionChange,
    fetchProfessions, fetchVersions, confirmRecalculate, confirmDeleteProfessionRules, formatDate,
  }
}
