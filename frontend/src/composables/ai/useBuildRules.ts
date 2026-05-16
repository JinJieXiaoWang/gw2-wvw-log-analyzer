import type { BuildExecutionData } from '@/composables/useAiAnalysis'

export type RuleCategory = 'weapon' | 'consumable' | 'profession' | 'skill' | 'general'

export interface BuildRuleResult {
  id: string
  label: string
  category: RuleCategory
  description: string
  status: 'pass' | 'fail' | 'warn'
  actual?: string
  expected?: string
}

export interface BuildRuleEngineResult {
  overallScore: number
  rules: BuildRuleResult[]
  categorySummary: Record<RuleCategory, { pass: number; fail: number; warn: number }>
}

const CATEGORY_LABELS: Record<RuleCategory, string> = {
  weapon: '武器配置',
  consumable: '消耗品',
  profession: '职业匹配',
  skill: '技能检查',
  general: '通用',
}

/**
 * 基于后端 BuildExecutionData 构建规则验证结果
 * 当后端返回 checks 时，自动分类并补充规则描述
 */
export function evaluateBuildRules(data: BuildExecutionData | null): BuildRuleEngineResult {
  if (!data?.execution_check?.checks?.length) {
    return {
      overallScore: data?.execution_score ?? 0,
      rules: [],
      categorySummary: { weapon: { pass: 0, fail: 0, warn: 0 }, consumable: { pass: 0, fail: 0, warn: 0 }, profession: { pass: 0, fail: 0, warn: 0 }, skill: { pass: 0, fail: 0, warn: 0 }, general: { pass: 0, fail: 0, warn: 0 } },
    }
  }

  const rules: BuildRuleResult[] = data.execution_check.checks.map((check, index) => {
    const category = inferCategory(check.label)
    const descriptions: Record<string, string> = {
      weapon: '主手/副手武器类型与职业Build要求匹配',
      consumable: '战斗前是否使用了正确的食物与增强道具',
      profession: '当前职业与Build配置要求一致',
      skill: '关键效用技能或精英技能已装备',
      general: '通用执行检查项',
    }
    return {
      id: `rule-${index}`,
      label: check.label,
      category,
      description: descriptions[category],
      status: check.status === 'pass' ? 'pass' : check.status === 'fail' ? 'fail' : 'warn',
      actual: check.actual,
      expected: check.status === 'pass' ? undefined : '符合预期',
    }
  })

  // 补充本地默认规则（当后端未覆盖时）
  const existingLabels = new Set(rules.map(r => r.label))
  const toStatus = (has: boolean): 'pass' | 'warn' => has ? 'pass' : 'warn'
  const defaultRules = [
    { id: 'default-food', label: '食物增益', category: 'consumable' as RuleCategory, description: '战斗中应保持食物增益覆盖', status: toStatus(existingLabels.has('食物增益')) },
    { id: 'default-utility', label: '增强道具', category: 'consumable' as RuleCategory, description: '战斗中应保持磨刀石/油/调谐覆盖', status: toStatus(existingLabels.has('增强道具')) },
    { id: 'default-weapon', label: '武器非空', category: 'weapon' as RuleCategory, description: '主手与副手武器槽不能空置', status: toStatus(existingLabels.has('武器非空')) },
  ].filter(r => !existingLabels.has(r.label)) as BuildRuleResult[]

  const allRules = [...rules, ...defaultRules]

  const categorySummary: Record<RuleCategory, { pass: number; fail: number; warn: number }> = {
    weapon: { pass: 0, fail: 0, warn: 0 },
    consumable: { pass: 0, fail: 0, warn: 0 },
    profession: { pass: 0, fail: 0, warn: 0 },
    skill: { pass: 0, fail: 0, warn: 0 },
    general: { pass: 0, fail: 0, warn: 0 },
  }

  allRules.forEach(r => {
    categorySummary[r.category][r.status]++
  })

  return {
    overallScore: data.execution_score,
    rules: allRules,
    categorySummary,
  }
}

function inferCategory(label: string): RuleCategory {
  const lower = label.toLowerCase()
  if (lower.includes('武器') || lower.includes('weapon') || lower.includes('主手') || lower.includes('副手')) return 'weapon'
  if (lower.includes('食物') || lower.includes('油') || lower.includes('磨刀石') || lower.includes('调谐') || lower.includes('utility') || lower.includes('consumable') || lower.includes('food') || lower.includes('增强')) return 'consumable'
  if (lower.includes('职业') || lower.includes('profession') || lower.includes('specialization')) return 'profession'
  if (lower.includes('技能') || lower.includes('skill') || lower.includes('trait')) return 'skill'
  return 'general'
}

export { CATEGORY_LABELS }
