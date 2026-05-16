/**
 * useScoringRulesSettings - 设置模块评分规则 composable（兼容 wrapper）
 * 基于统一版本，关闭可选功能，并包装差异接口以完全保持原有行为
 */

import { RoleType } from '@/constants/dictValues'
import { computed } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useScoringRules as useScoringRulesBase } from '@/composables/scoring/useScoringRules'
import { scoringRulesService } from '@/services/core/scoringRulesService'
import { configManager } from '@/services/core/configManager'

export const ROLE_TYPES = [
  { type: RoleType.DPS, label: '输出', description: '伤害输出职责', icon: 'pi pi-bolt' },
  { type: RoleType.SUPPORT, label: '辅助', description: '治疗增益职责', icon: 'pi pi-heart' },
  { type: RoleType.TANK, label: '承伤', description: '吸收伤害职责', icon: 'pi pi-shield' }
]

export const GRADE_LEVELS = [
  { letter: 'S', range: '≥90分', desc: '表现卓越', gradient: 'linear-gradient(135deg, #FFD700, #FFA500)' },
  { letter: 'A', range: '≥80分', desc: '表现优秀', gradient: 'linear-gradient(135deg, #00D68F, #00B4FF)' },
  { letter: 'B', range: '≥70分', desc: '表现良好', gradient: 'linear-gradient(135deg, #165DFF, #8B5CF6)' },
  { letter: 'C', range: '≥60分', desc: '表现一般', gradient: 'linear-gradient(135deg, #FFAA00, #FFB347)' },
  { letter: 'D', range: '≥40分', desc: '表现较差', gradient: 'linear-gradient(135deg, #FF8A65, #FF5722)' },
  { letter: 'F', range: '<40分', desc: '表现很差', gradient: 'linear-gradient(135deg, #FF4D6A, #D93664)' }
]

export function useScoringRulesSettings() {
  const confirm = useConfirm()
  const toast = useToast()

  const base = useScoringRulesBase({
    enableProfessionRules: false,
    enableRecalculation: false,
    enableVersionHistory: false,
  })

  // 保持原有默认角色
  if (!base.activeRole.value) base.activeRole.value = RoleType.DPS

  // ========== 包装差异计算属性 ==========
  const weightStatus = computed(() => {
    const cls = base.weightStatusClass.value
    if (cls === 'optimal') return { bg: 'bg-success/10', text: 'text-success', bar: 'bg-success' }
    if (cls === 'warning') return { bg: 'bg-warning/10', text: 'text-warning', bar: 'bg-warning' }
    return { bg: 'bg-error/10', text: 'text-error', bar: 'bg-error' }
  })

  function roleIconBgClass(role: string) {
    const map: Record<string, string> = {
      [RoleType.DPS]: 'bg-gradient-to-br from-error to-orange-500',
      [RoleType.SUPPORT]: 'bg-gradient-to-br from-success to-info',
      [RoleType.TANK]: 'bg-gradient-to-br from-purple-500 to-primary'
    }
    return map[role] || 'bg-gradient-to-br from-primary to-secondary'
  }

  // ========== 包装差异动作 ==========
  function removeRule(index: number) {
    confirm.require({
      message: '确定要删除这条评分规则吗？',
      header: '删除确认',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        base.editableRules.value.splice(index, 1)
        base.markChanged()
        toast.add({ severity: 'success', summary: '成功', detail: '删除成功', life: configManager.get('ui').toastLife })
      }
    })
  }

  function addRule() {
    if (!base.newRuleDimension.value) return
    base.editableRules.value.push({
      role_type: base.activeRole.value,
      dimension: base.newRuleDimension.value,
      weight: base.newRuleWeight.value / 100,
      description: base.newRuleDesc.value,
      is_active: true,
      sort_order: base.editableRules.value.length + 1
    } as any)
    base.markChanged()
    base.newRuleDimension.value = ''
    base.newRuleWeight.value = 10
    base.newRuleDesc.value = ''
    toast.add({ severity: 'success', summary: '成功', detail: '添加成功', life: configManager.get('ui').toastLife })
  }

  function resetChanges() {
    if (!base.hasUnsavedChanges(base.activeRole.value)) return
    confirm.require({
      message: '确定要取消所有未保存的更改吗？',
      header: '取消确认',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        base.currentRules.value[base.activeRole.value] = JSON.parse(JSON.stringify(base.originalRules.value[base.activeRole.value] || []))
        base.changedRoles.value.delete(base.activeRole.value)
        base.syncEditableRules()
        toast.add({ severity: 'info', summary: '已取消', detail: '已恢复到上次保存的状态', life: configManager.get('ui').toastLife })
      }
    })
  }

  async function saveChanges() {
    if (!base.hasUnsavedChanges(base.activeRole.value)) return
    base.saving.value = true
    try {
      await scoringRulesService.batchUpdate(base.activeRole.value, base.editableRules.value)
      base.originalRules.value[base.activeRole.value] = JSON.parse(JSON.stringify(base.editableRules.value))
      base.changedRoles.value.delete(base.activeRole.value)
      toast.add({ severity: 'success', summary: '成功', detail: '保存成功', life: configManager.get('ui').toastLife })
    } catch (e: unknown) {
      toast.add({ severity: 'error', summary: '错误', detail: e instanceof Error ? e.message : '保存失败', life: configManager.get('ui').toastErrorLife })
    } finally {
      base.saving.value = false
    }
  }

  function confirmReset() {
    confirm.require({
      message: '确定要重置为默认评分规则吗？这将覆盖所有自定义设置。',
      header: '重置确认',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        base.loading.value = true
        try {
          await scoringRulesService.resetDefault(base.activeRole.value)
          await base.fetchRules()
          base.changedRoles.value.delete(base.activeRole.value)
          toast.add({ severity: 'success', summary: '成功', detail: '已重置为默认规则', life: configManager.get('ui').toastLife })
        } catch (e: unknown) {
          toast.add({ severity: 'error', summary: '错误', detail: e instanceof Error ? e.message : '重置失败', life: configManager.get('ui').toastErrorLife })
        } finally {
          base.loading.value = false
        }
      }
    })
  }

  // ========== Return ==========
  return {
    activeRole: base.activeRole,
    loading: base.loading,
    saving: base.saving,
    editableRules: base.editableRules,
    changedRoles: base.changedRoles,
    allDimensions: base.allDimensions,
    newRuleDimension: base.newRuleDimension,
    newRuleWeight: base.newRuleWeight,
    newRuleDesc: base.newRuleDesc,
    totalWeight: base.totalWeight,
    availableDimensions: base.availableDimensions,
    weightStatus,
    roleIconBgClass,
    hasUnsavedChanges: base.hasUnsavedChanges,
    getDimensionIcon: base.getDimensionIcon,
    getDimensionColor: base.getDimensionColor,
    getDimensionLabel: base.getDimensionLabel,
    fetchRules: base.fetchRules,
    fetchDimensions: base.fetchDimensions,
    syncEditableRules: base.syncEditableRules,
    switchRole: base.switchRole,
    markChanged: base.markChanged,
    moveUp: base.moveUp,
    moveDown: base.moveDown,
    removeRule,
    addRule,
    resetChanges,
    saveChanges,
    confirmReset,
  }
}
