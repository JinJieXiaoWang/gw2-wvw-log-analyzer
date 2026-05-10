import { ref, computed } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { scoringRulesService, type ScoringRule, type DimensionInfo } from '@/services/scoring/scoringRulesService'
import { configManager } from '@/services/core/configManager'

export const ROLE_TYPES = [
  { type: 'dps', label: '输出', description: '伤害输出职责', icon: 'pi pi-bolt' },
  { type: 'support', label: '辅助', description: '治疗增益职责', icon: 'pi pi-heart' },
  { type: 'tank', label: '承伤', description: '吸收伤害职责', icon: 'pi pi-shield' }
]

export const GRADE_LEVELS = [
  { letter: 'S', range: '≥90分', desc: '表现卓越', gradient: 'linear-gradient(135deg, #FFD700, #FFA500)' },
  { letter: 'A', range: '≥80分', desc: '表现优秀', gradient: 'linear-gradient(135deg, #00D68F, #00B4FF)' },
  { letter: 'B', range: '≥70分', desc: '表现良好', gradient: 'linear-gradient(135deg, #165DFF, #8B5CF6)' },
  { letter: 'C', range: '≥60分', desc: '表现一般', gradient: 'linear-gradient(135deg, #FFAA00, #FFB347)' },
  { letter: 'D', range: '≥40分', desc: '表现较差', gradient: 'linear-gradient(135deg, #FF8A65, #FF5722)' },
  { letter: 'F', range: '<40分', desc: '表现很差', gradient: 'linear-gradient(135deg, #FF4D6A, #D93664)' }
]

const DIMENSION_ICONS: Record<string, string> = {
  damage: 'pi pi-bolt', healing: 'pi pi-heart', protection: 'pi pi-shield',
  crowd_control: 'pi pi-lock', support: 'pi pi-star', survival: 'pi pi-users',
  objective: 'pi pi-flag', downstacks: 'pi pi-arrow-down'
}

const DIMENSION_COLORS: Record<string, string> = {
  damage: '#FF4D6A', healing: '#00D68F', protection: '#165DFF',
  crowd_control: '#9D4EDD', support: '#FFAA00', survival: '#00B4FF',
  objective: '#4CAF50', downstacks: '#FF5722'
}

export function useScoringRulesSettings() {
  const confirm = useConfirm()
  const toast = useToast()

  const activeRole = ref('dps')
  const loading = ref(false)
  const saving = ref(false)
  const currentRules = ref<Record<string, ScoringRule[]>>({})
  const originalRules = ref<Record<string, ScoringRule[]>>({})
  const editableRules = ref<ScoringRule[]>([])
  const changedRoles = ref<Set<string>>(new Set())
  const allDimensions = ref<DimensionInfo[]>([])
  const newRuleDimension = ref('')
  const newRuleWeight = ref(10)
  const newRuleDesc = ref('')

  const totalWeight = computed(() => editableRules.value.filter(r => r.is_active).reduce((s, r) => s + (r.weight || 0), 0))
  const availableDimensions = computed(() => {
    const used = new Set(editableRules.value.map(r => r.dimension))
    return allDimensions.value.filter(d => !used.has(d.key))
  })

  const weightStatus = computed(() => {
    const diff = Math.abs(totalWeight.value - 1.0)
    if (diff < 0.01) return { bg: 'bg-success/10', text: 'text-success', bar: 'bg-success' }
    if (diff < 0.1) return { bg: 'bg-warning/10', text: 'text-warning', bar: 'bg-warning' }
    return { bg: 'bg-error/10', text: 'text-error', bar: 'bg-error' }
  })

  function roleIconBgClass(role: string) {
    const map: Record<string, string> = { dps: 'bg-gradient-to-br from-error to-orange-500', support: 'bg-gradient-to-br from-success to-info', tank: 'bg-gradient-to-br from-purple-500 to-primary' }
    return map[role] || 'bg-gradient-to-br from-primary to-secondary'
  }

  function hasUnsavedChanges(role: string) { return changedRoles.value.has(role) }
  function getDimensionIcon(key: string) { return DIMENSION_ICONS[key] || 'pi pi-circle' }
  function getDimensionColor(key: string) { return DIMENSION_COLORS[key] || '#888888' }
  function getDimensionLabel(key: string) { return allDimensions.value.find(d => d.key === key)?.label || key }

  async function fetchRules() {
    loading.value = true
    try {
      const data = await scoringRulesService.getRules()
      if (data) {
        for (const key of ['dps', 'support', 'tank']) {
          if (data[key]) {
            currentRules.value[key] = data[key].rules || []
            originalRules.value[key] = JSON.parse(JSON.stringify(data[key].rules || []))
          }
        }
      }
      syncEditableRules()
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分规则失败', life: configManager.get('ui').toastErrorLife })
    } finally { loading.value = false }
  }

  async function fetchDimensions() {
    try { allDimensions.value = await scoringRulesService.getDimensions() } catch (e) { console.error('获取评分维度失败', e) }
  }

  function syncEditableRules() {
    const rules = currentRules.value[activeRole.value] || []
    editableRules.value = rules.map(r => ({ ...r }))
  }

  function switchRole(role: string) { activeRole.value = role; syncEditableRules() }
  function markChanged() { changedRoles.value.add(activeRole.value) }

  function moveUp(index: number) {
    if (index === 0) return
    const temp = editableRules.value[index]
    editableRules.value[index] = editableRules.value[index - 1]
    editableRules.value[index - 1] = temp
    markChanged()
  }

  function moveDown(index: number) {
    if (index === editableRules.value.length - 1) return
    const temp = editableRules.value[index]
    editableRules.value[index] = editableRules.value[index + 1]
    editableRules.value[index + 1] = temp
    markChanged()
  }

  function removeRule(index: number) {
    confirm.require({
      message: '确定要删除这条评分规则吗？', header: '删除确认', icon: 'pi pi-exclamation-triangle',
      accept: () => { editableRules.value.splice(index, 1); markChanged(); toast.add({ severity: 'success', summary: '成功', detail: '删除成功', life: configManager.get('ui').toastLife }) }
    })
  }

  function addRule() {
    if (!newRuleDimension.value) return
    editableRules.value.push({
      role_type: activeRole.value, dimension: newRuleDimension.value,
      weight: newRuleWeight.value / 100, description: newRuleDesc.value,
      is_active: true, sort_order: editableRules.value.length + 1
    } as ScoringRule)
    markChanged()
    newRuleDimension.value = ''; newRuleWeight.value = 10; newRuleDesc.value = ''
    toast.add({ severity: 'success', summary: '成功', detail: '添加成功', life: configManager.get('ui').toastLife })
  }

  function resetChanges() {
    if (!hasUnsavedChanges(activeRole.value)) return
    confirm.require({
      message: '确定要取消所有未保存的更改吗？', header: '取消确认', icon: 'pi pi-exclamation-triangle',
      accept: () => {
        currentRules.value[activeRole.value] = JSON.parse(JSON.stringify(originalRules.value[activeRole.value] || []))
        changedRoles.value.delete(activeRole.value)
        syncEditableRules()
        toast.add({ severity: 'info', summary: '已取消', detail: '已恢复到上次保存的状态', life: configManager.get('ui').toastLife })
      }
    })
  }

  async function saveChanges() {
    if (!hasUnsavedChanges(activeRole.value)) return
    saving.value = true
    try {
      await scoringRulesService.batchUpdate(activeRole.value, editableRules.value)
      originalRules.value[activeRole.value] = JSON.parse(JSON.stringify(editableRules.value))
      changedRoles.value.delete(activeRole.value)
      toast.add({ severity: 'success', summary: '成功', detail: '保存成功', life: configManager.get('ui').toastLife })
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '错误', detail: e?.message || '保存失败', life: configManager.get('ui').toastErrorLife })
    } finally { saving.value = false }
  }

  function confirmReset() {
    confirm.require({
      message: '确定要重置为默认评分规则吗？这将覆盖所有自定义设置。', header: '重置确认', icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        loading.value = true
        try {
          await scoringRulesService.resetDefault(activeRole.value)
          await fetchRules()
          changedRoles.value.delete(activeRole.value)
          toast.add({ severity: 'success', summary: '成功', detail: '已重置为默认规则', life: configManager.get('ui').toastLife })
        } catch (e: any) {
          toast.add({ severity: 'error', summary: '错误', detail: e?.message || '重置失败', life: configManager.get('ui').toastErrorLife })
        } finally { loading.value = false }
      }
    })
  }

  return {
    activeRole, loading, saving, editableRules, changedRoles, allDimensions,
    newRuleDimension, newRuleWeight, newRuleDesc,
    totalWeight, availableDimensions, weightStatus,
    roleIconBgClass, hasUnsavedChanges,
    getDimensionIcon, getDimensionColor, getDimensionLabel,
    fetchRules, fetchDimensions, syncEditableRules,
    switchRole, markChanged, moveUp, moveDown, removeRule, addRule,
    resetChanges, saveChanges, confirmReset
  }
}
